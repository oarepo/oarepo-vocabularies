# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Datastream writers for the ORCID public data file.

The writer bypasses the vocabulary service on purpose: creating 20M records through
``service.create()`` costs one validation, one transaction and one index request per
record. Instead, a whole batch is written with a single ``INSERT ... ON CONFLICT`` and
a single ``_bulk`` request.

Because the service is bypassed, the writer has to produce exactly what the service and
the indexer would have produced:

* the database json as stored by the names service (``name`` computed from the given and
  family name, affiliations with an id reduced to ``{"id": ...}``),
* only affiliation ids that exist in the affiliations vocabulary, otherwise Invenio fails
  to read or index the record (see :mod:`oarepo_vocabularies.orcid.affiliations`),
* the index document as dumped by the record's ``SearchDumper`` (``uuid``, ``version_id``,
  ``created``, ``updated``, dereferenced affiliations), sent to the prefixed index alias
  with the same external versioning as ``RecordIndexer``.
"""

# datastream components implement the framework base-class signatures, which pass
# arguments they do not necessarily use
# ruff: noqa: ARG002

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, TypedDict

from invenio_db import db
from invenio_search import current_search_client
from invenio_search.engine import search
from invenio_search.utils import build_alias_name
from invenio_vocabularies.datastreams.writers import BaseWriter
from sqlalchemy import literal_column
from sqlalchemy.dialects.postgresql import insert as pg_insert

from oarepo_vocabularies.orcid.affiliations import resolve_affiliations

if TYPE_CHECKING:
    from collections.abc import Mapping

    from invenio_vocabularies.datastreams.datastreams import StreamEntry

    from oarepo_vocabularies.orcid.affiliations import AffiliationRef


class NameRow(TypedDict):
    """A row of the ``name_metadata`` table, as inserted by :class:`NamesBulkWriter`."""

    id: uuid.UUID
    pid: str
    json: dict[str, Any]
    version_id: int
    created: datetime
    updated: datetime
    internal_id: str | None


UUID_NAMESPACE = uuid.UUID("6f1c0d9e-5b0a-4c1e-9b2e-0f0f5b0e0001")
"""Fixed namespace for record identifiers derived from ORCID iDs."""


def record_uuid(orcid: str) -> uuid.UUID:
    """Return the record identifier for an ORCID iD.

    The identifier is derived from the iD instead of being random so that writing the
    same entry twice (a redelivered Celery message, a re-run of the import) updates
    the same row and the same index document instead of duplicating them.
    """
    return uuid.uuid5(UUID_NAMESPACE, orcid)


def affiliation_ids(entry: Mapping[str, Any]) -> set[str]:
    """Return the affiliation ids referenced by a transformed entry."""
    return {aff["id"] for aff in entry.get("affiliations") or [] if aff.get("id")}


def normalize_entry(
    entry: Mapping[str, Any],
    *,
    schema: str,
    known_affiliations: Mapping[str, AffiliationRef],
) -> dict[str, Any]:
    """Return the database json the names service would store for the entry.

    Mirrors ``NameSchema`` (``name`` = "family, given") and ``RelationsComponent`` (an
    affiliation with an id is stored as ``{"id": ...}``). Affiliation ids missing from the
    vocabulary are dropped and only the organization name is kept.
    """
    # the pid lives in the `pid` column only, the service does not store it in the json
    data = {key: value for key, value in entry.items() if value is not None and key != "id"}
    data["$schema"] = schema

    family_name, given_name = data.get("family_name"), data.get("given_name")
    if family_name and given_name:
        data["name"] = f"{family_name}, {given_name}"
    elif family_name:
        # NameSchema requires `name` when there is no given name
        data["name"] = family_name

    affiliations: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for affiliation in entry.get("affiliations") or []:
        aff_id, name = affiliation.get("id"), affiliation.get("name")
        if aff_id and aff_id in known_affiliations:
            if aff_id not in seen_ids:
                seen_ids.add(aff_id)
                affiliations.append({"id": aff_id})
        elif name and name not in seen_names:
            seen_names.add(name)
            affiliations.append({"name": name})
    data["affiliations"] = affiliations
    return data


def build_index_document(  # noqa: PLR0913 - keyword-only parts of the record model
    data: Mapping[str, Any],
    *,
    pid: str,
    record_id: uuid.UUID,
    version_id: int,
    created: datetime,
    updated: datetime,
    known_affiliations: Mapping[str, AffiliationRef],
    now: datetime,
) -> dict[str, Any]:
    """Return the document the names ``SearchDumper`` would produce for the record."""
    document = dict(data)
    document["affiliations"] = [
        known_affiliations[aff["id"]].dereferenced() if "id" in aff else dict(aff)
        for aff in data.get("affiliations", [])
    ]
    document.update(
        {
            "id": pid,
            "uuid": str(record_id),
            "version_id": version_id,
            "created": created.isoformat(),
            "updated": updated.isoformat(),
            "indexed_at": now.isoformat(),
        }
    )
    return document


def _names_record_type() -> Any:
    """Return the ``names`` record type (imported lazily to keep import time low)."""
    from invenio_vocabularies.contrib.names.names import (
        record_type,
    )

    return record_type


class NamesBulkWriter(BaseWriter):
    """Write name entries in bulk, one database and one index request per batch.

    Registered as ``names-bulk``. The ``async`` writer passes the ``args`` of this
    writer to a Celery task and the task constructs it again on the worker, therefore
    the constructor may only accept plain arguments.
    """

    def __init__(
        self,
        update: bool = False,
        chunk_size: int = 2000,
        fetch_missing_affiliations: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the writer.

        :param update: update records that already exist instead of ignoring them.
        :param chunk_size: number of documents per ``_bulk`` request.
        :param fetch_missing_affiliations: import affiliations missing from the
            vocabulary from the ROR API.
        """
        super().__init__(*args, **kwargs)
        self._update = update
        self._chunk_size = chunk_size
        self._fetch_missing_affiliations = fetch_missing_affiliations

    def write(self, stream_entry: StreamEntry, *args: Any, **kwargs: Any) -> StreamEntry:
        """Write a single entry (the datastream normally uses :meth:`write_many`)."""
        self.write_many([stream_entry])
        return stream_entry

    def write_many(self, stream_entries: list[StreamEntry], *args: Any, **kwargs: Any) -> list[StreamEntry]:
        """Write a batch of entries with one database and one index request."""
        # one row per ORCID iD: ON CONFLICT can not touch the same row twice in a statement
        by_pid: dict[str, StreamEntry] = {}
        for stream_entry in stream_entries:
            if not stream_entry.errors:
                by_pid[stream_entry.entry["id"]] = stream_entry
        if not by_pid:
            return stream_entries

        record_type = _names_record_type()
        known = resolve_affiliations(
            set().union(*(affiliation_ids(se.entry) for se in by_pid.values())),
            fetch_missing=self._fetch_missing_affiliations,
        )
        now = datetime.now(UTC)
        rows: list[NameRow] = [
            {
                "id": record_uuid(pid),
                "pid": pid,
                "json": normalize_entry(se.entry, schema=record_type.schema_path, known_affiliations=known),
                "version_id": 1,
                "created": now,
                "updated": now,
                "internal_id": None,
            }
            for pid, se in by_pid.items()
        ]

        written = self._write_rows(rows, record_type.model_cls.__table__)

        # index only what was written; a skipped row keeps its current index document
        index = build_alias_name(record_type.index_name)
        actions = []
        for row in rows:
            result = written.get(row["id"])
            if result is None:
                continue
            by_pid[row["pid"]].op_type = "create" if result["inserted"] else "update"
            actions.append(
                {
                    "_op_type": "index",
                    "_index": index,
                    "_id": str(row["id"]),
                    # the same external versioning as RecordIndexer (revision_id)
                    "_version": result["version_id"] - 1,
                    "_version_type": "external_gte",
                    "_source": build_index_document(
                        row["json"],
                        pid=row["pid"],
                        record_id=row["id"],
                        version_id=result["version_id"],
                        created=result["created"],
                        updated=result["updated"],
                        known_affiliations=known,
                        now=now,
                    ),
                }
            )

        if actions:
            search.helpers.bulk(current_search_client, actions, chunk_size=self._chunk_size, refresh=False)
        return stream_entries

    def _write_rows(self, rows: list[NameRow], table: Any) -> dict[uuid.UUID, dict[str, Any]]:
        """Insert the rows, ignoring or updating entries that already exist.

        Returns the written rows (id -> version_id, created, updated, inserted). Rows
        skipped because they already exist (``update=False``) are not returned.
        """
        statement = pg_insert(table).values(rows)
        if self._update:
            statement = statement.on_conflict_do_update(
                index_elements=["pid"],
                set_={
                    "json": statement.excluded.json,
                    "updated": statement.excluded.updated,
                    "version_id": table.c.version_id + 1,
                },
            )
        else:
            statement = statement.on_conflict_do_nothing(index_elements=["pid"])
        statement = statement.returning(
            table.c.id,
            table.c.version_id,
            table.c.created,
            table.c.updated,
            # xmax is 0 for a freshly inserted row and set for an updated one
            literal_column("(xmax = 0)").label("inserted"),
        )
        result = {row.id: row._asdict() for row in db.session.execute(statement)}
        db.session.commit()
        return result


VOCABULARIES_DATASTREAM_WRITERS = {"names-bulk": NamesBulkWriter}
"""Writers contributed by :mod:`oarepo_vocabularies.orcid`."""

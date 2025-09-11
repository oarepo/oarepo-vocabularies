#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Fixtures for vocabularies."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

from invenio_db import db
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.models import AffiliationsMetadata
from invenio_vocabularies.contrib.awards.models import AwardsMetadata
from invenio_vocabularies.contrib.funders.models import FundersMetadata
from invenio_vocabularies.contrib.names.models import NamesMetadata
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.writers import BaseWriter, ServiceWriter
from invenio_vocabularies.records.api import VocabularyType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from flask_principal import Identity


def vocabularies_generator(service_id: str, **kwargs: Any) -> Iterable:  # noqa: ARG001
    """Generate loaders and dumpers for all vocabularies."""
    vocabularies = VocabularyType.query.all()
    for vocab_type in vocabularies:
        loader = [
            {
                "writer": "vocabulary",
                "vocabulary": vocab_type.id,
                "pid_type": vocab_type.pid_type,
            },
            {"source": f"vocabulary-{vocab_type.id}.yaml"},
        ]

        dumper = [
            {"reader": "vocabulary", "vocabulary": vocab_type.id},
            {"writer": "yaml", "target": f"vocabulary-{vocab_type.id}.yaml"},
        ]
        yield f"vocabulary-{vocab_type.id}", loader, dumper


class VocabularyReader(BaseReader):
    """Reader for vocabularies."""

    def __init__(self, *, vocabulary: str | None = None, identity: Identity | None = None, **kwargs: Any) -> None:
        """Initialize the VocabularyReader."""
        super().__init__(service="vocabularies", identity=identity, **kwargs)
        self.vocabulary = vocabulary

    def __iter__(self):
        """Iterate over vocabulary entries and yield specific vocabulary type."""
        # invenio-vocabularies has no filter on type id, so need to scan everything
        # hopefully this is not a too frequent op
        for rec in self._service.scan(self._identity):
            if rec["type"] == self.vocabulary:
                rec_tmp = dict(rec)
                rec_tmp.pop("type")
                yield StreamEntry(rec_tmp)


class VocabularyWriter(ServiceWriter):
    """Writer for vocabularies."""

    def __init__(
        self,
        *,
        vocabulary: str | None = None,
        pid_type: str | None = None,
        identity: Identity | None = None,
        update: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the VocabularyWriter."""
        super().__init__(service="vocabularies", identity=identity, update=update, **kwargs)
        self.vocabulary = vocabulary
        self.pid_type = pid_type
        vt = VocabularyType.query.filter_by(id=self.vocabulary).one_or_none()
        if not vt:
            vt = VocabularyType(id=self.vocabulary, pid_type=self.pid_type)
            db.session.add(vt)
            db.session.commit()

    def write(self, stream_batch: StreamEntry, *args: Any, **kwargs: Any) -> StreamEntry:
        """Write the input entry using a given service to the target output."""
        for stream_entry in stream_batch.entries:
            entry = stream_entry.entry
            entry["type"] = self.vocabulary
        return super().write(stream_batch, *args, **kwargs)

    def _get_stream_entry_id(self, entry: StreamEntry) -> tuple | None:
        _id = entry.entry.get("id", None)
        if _id:
            return (self.vocabulary, _id)
        return None


class AwardsWriter(BaseWriter):
    """Optimized writer for awards."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the AwardsWriter."""
        super().__init__(**kwargs)

    def write(self, batch: StreamEntry) -> Any:
        """Write the input entry to the target output."""
        awards_service = current_service_registry.get("awards")

        awards = []
        for entry in batch.ok_entries:
            payload = entry.entry
            stored = AwardsMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                awards.append(stored)
                continue

            pid = payload.pop("id")
            if "funder" in payload:
                funder_id = payload["funder"].get("id")
                payload["funder"]["name"] = self.lookup_funder_name(funder_id)
            award = AwardsMetadata(pid=pid, json=payload)
            db.session.add(award)
            awards.append(award)
            entry.id = award.pid

        db.session.commit()
        awards_service.indexer.bulk_index([award.id for award in awards])

        return batch

    def finish(self) -> None:
        """Finish the writing process."""

    @functools.lru_cache(maxsize=1024)  # noqa: B019
    def lookup_funder_name(self, funder_id: str) -> Any:
        """Lookup funder name by id."""
        funder = FundersMetadata.query.filter_by(pid=funder_id).one()
        return funder.json["name"]


class NamesWriter(BaseWriter):
    """Optimized writer for names."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the NamesWriter."""
        super().__init__(**kwargs)

    def write(self, batch: StreamEntry) -> Any:
        """Write the input entry to the target output."""
        names_service = current_service_registry.get("names")

        names = []
        for entry in batch.ok_entries:
            payload = entry.entry
            if "affiliations" in payload:
                raise Exception("Affiliations are not supported in this writer")  # noqa: TRY002
            stored = NamesMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                names.append(stored)
                continue

            pid = payload.pop("id")
            name = NamesMetadata(pid=pid, json=payload)
            db.session.add(name)
            names.append(name)
            entry.id = name.pid

        db.session.commit()
        names_service.indexer.bulk_index([name.id for name in names])

        return batch

    def finish(self) -> Any:
        """Finish the writing process."""


class AffiliationsWriter(BaseWriter):
    """Optimized writer for awards."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the AffiliationsWriter."""
        super().__init__(**kwargs)

    def write(self, batch: StreamEntry) -> Any:
        """Write the input entry to the target output."""
        affiliations_service = current_service_registry.get("affiliations")

        affiliations = []
        for entry in batch.ok_entries:
            payload = entry.entry
            stored = AffiliationsMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                affiliations.append(stored)
                continue

            pid = payload.pop("id")
            affiliation = AffiliationsMetadata(pid=pid, json=payload)
            db.session.add(affiliation)
            affiliations.append(affiliation)
            entry.id = affiliation.pid

        db.session.commit()
        affiliations_service.indexer.bulk_index([affiliation.id for affiliation in affiliations])

        return batch

    def finish(self) -> Any:
        """Finish the writing process."""

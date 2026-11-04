# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Unit tests for the bulk writer of name records (no database, no search engine)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from flask import Flask
from invenio_vocabularies.datastreams.datastreams import StreamEntry

from oarepo_vocabularies.orcid import writers as writers_module
from oarepo_vocabularies.orcid.affiliations import AffiliationRef
from oarepo_vocabularies.orcid.writers import (
    NamesBulkWriter,
    build_index_document,
    normalize_entry,
    record_uuid,
)

ENTRY = {
    "id": "0000-0002-1825-0097",
    "given_name": "Josiah",
    "family_name": "Carberry",
    "identifiers": [{"scheme": "orcid", "identifier": "0000-0002-1825-0097"}],
    "affiliations": [
        {"name": "Brown University", "id": "05gq02987"},
        {"name": "Unknown Org", "id": "000000000"},
        {"name": "Wesleyan"},
    ],
}
SCHEMA = "local://names/name-v1.0.0.json"
INDEX = "names-name-v2.0.0"
PREFIX = "nma-"
BROWN = AffiliationRef(
    pid="05gq02987",
    uuid="11111111-1111-1111-1111-111111111111",
    version_id=3,
    name="Brown University",
    acronym="BU",
)
KNOWN = {BROWN.pid: BROWN}
NOW = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def app_ctx():
    """Provide an application context with an index prefix, like a real instance."""
    app = Flask(__name__)
    app.config["SEARCH_INDEX_PREFIX"] = PREFIX
    with app.app_context():
        yield app


def test_record_uuid_is_deterministic():
    assert record_uuid(ENTRY["id"]) == record_uuid(ENTRY["id"])
    assert record_uuid(ENTRY["id"]) != record_uuid("0000-0002-1825-0098")


def test_normalize_entry_matches_the_names_service():
    data = normalize_entry(ENTRY, schema=SCHEMA, known_affiliations=KNOWN)

    assert data["name"] == "Carberry, Josiah"
    assert data["$schema"] == SCHEMA
    assert "id" not in data
    # known id -> id only (as RelationsComponent stores it); unknown id -> name only
    assert data["affiliations"] == [{"id": "05gq02987"}, {"name": "Unknown Org"}, {"name": "Wesleyan"}]


def test_normalize_entry_without_given_name():
    data = normalize_entry(
        {**ENTRY, "given_name": None, "affiliations": []},
        schema=SCHEMA,
        known_affiliations={},
    )

    assert data["name"] == "Carberry"
    assert "given_name" not in data


def test_normalize_entry_deduplicates_affiliations():
    entry = {
        **ENTRY,
        "affiliations": [
            {"name": "Brown University", "id": "05gq02987"},
            {"name": "Brown", "id": "05gq02987"},
            {"name": "X"},
            {"name": "X", "id": "missing"},
        ],
    }

    data = normalize_entry(entry, schema=SCHEMA, known_affiliations=KNOWN)

    assert data["affiliations"] == [{"id": "05gq02987"}, {"name": "X"}]


def test_build_index_document_matches_the_search_dumper():
    data = normalize_entry(ENTRY, schema=SCHEMA, known_affiliations=KNOWN)
    record_id = record_uuid(ENTRY["id"])

    document = build_index_document(
        data,
        pid=ENTRY["id"],
        record_id=record_id,
        version_id=2,
        created=NOW,
        updated=NOW,
        known_affiliations=KNOWN,
        now=NOW,
    )

    assert document["id"] == ENTRY["id"]
    assert document["uuid"] == str(record_id)
    assert document["version_id"] == 2
    assert document["created"] == NOW.isoformat()
    assert document["updated"] == NOW.isoformat()
    assert document["indexed_at"] == NOW.isoformat()
    assert document["name"] == "Carberry, Josiah"
    assert document["affiliations"] == [
        {
            "id": "05gq02987",
            "name": "Brown University",
            "acronym": "BU",
            "@v": "11111111-1111-1111-1111-111111111111::2",
        },
        {"name": "Unknown Org"},
        {"name": "Wesleyan"},
    ]
    # the database json must not be modified by the dereferencing
    assert data["affiliations"][0] == {"id": "05gq02987"}


def _capturing_writer(monkeypatch, *, update: bool = False, existing: frozenset[str] = frozenset(), **kwargs):
    """Return a writer whose database and index writes are captured instead of executed.

    ``existing`` are ORCID iDs whose rows already exist in the fake database.
    """
    captured: dict = {"rows": [], "actions": [], "fetch_missing": None}

    def fake_resolve(ids, *, fetch_missing=True):
        captured["fetch_missing"] = fetch_missing
        captured["requested_ids"] = set(ids)
        return {pid: ref for pid, ref in KNOWN.items() if pid in ids}

    def fake_write_rows(self, rows, table):
        captured["rows"] = rows
        result = {}
        for row in rows:
            if row["pid"] in existing:
                if update:
                    result[row["id"]] = {"version_id": 5, "created": NOW, "updated": NOW, "inserted": False}
            else:
                result[row["id"]] = {"version_id": 1, "created": NOW, "updated": NOW, "inserted": True}
        return result

    def fake_bulk(client, actions, **kwargs):
        captured["actions"] = list(actions)

    monkeypatch.setattr(writers_module, "resolve_affiliations", fake_resolve)
    monkeypatch.setattr(NamesBulkWriter, "_write_rows", fake_write_rows)
    monkeypatch.setattr(writers_module.search.helpers, "bulk", fake_bulk)
    return NamesBulkWriter(update=update, **kwargs), captured


def test_write_many_writes_one_batch_and_sets_op_type(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch)
    entries = [StreamEntry(ENTRY), StreamEntry({**ENTRY, "id": "0000-0002-1825-0098"})]

    result = writer.write_many(entries)

    assert len(captured["rows"]) == 2
    assert len(captured["actions"]) == 2
    assert captured["requested_ids"] == {"05gq02987", "000000000"}
    # write_many_entry derives the run counters from op_type
    assert [entry.op_type for entry in result] == ["create", "create"]


def test_write_many_targets_the_prefixed_index_alias_with_external_versioning(monkeypatch):
    # the bare index name lacks SEARCH_INDEX_PREFIX: writing there makes the search
    # engine auto-create a new index with dynamic mappings instead of using the real one
    writer, captured = _capturing_writer(monkeypatch)

    writer.write_many([StreamEntry(ENTRY)])

    action = captured["actions"][0]
    assert action["_index"] == PREFIX + INDEX
    assert action["_id"] == str(record_uuid(ENTRY["id"]))
    # RecordIndexer indexes with version=revision_id (version_id - 1), external_gte
    assert action["_version"] == 0
    assert action["_version_type"] == "external_gte"
    assert action["_source"]["uuid"] == str(record_uuid(ENTRY["id"]))


def test_write_many_skips_existing_rows_without_update(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch, existing=frozenset({ENTRY["id"]}))
    other = StreamEntry({**ENTRY, "id": "0000-0002-1825-0098"})
    existing = StreamEntry(ENTRY)

    writer.write_many([existing, other])

    assert [action["_source"]["id"] for action in captured["actions"]] == ["0000-0002-1825-0098"]
    assert existing.op_type is None
    assert other.op_type == "create"


def test_write_many_reindexes_updated_rows_with_their_new_version(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch, update=True, existing=frozenset({ENTRY["id"]}))

    result = writer.write_many([StreamEntry(ENTRY)])

    assert result[0].op_type == "update"
    assert captured["actions"][0]["_version"] == 4
    assert captured["actions"][0]["_source"]["version_id"] == 5


def test_write_many_deduplicates_orcid_ids(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch)

    writer.write_many([StreamEntry(ENTRY), StreamEntry({**ENTRY, "given_name": "J."})])

    assert len(captured["rows"]) == 1
    assert captured["rows"][0]["json"]["given_name"] == "J."


def test_write_many_skips_entries_with_errors(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch)
    broken = StreamEntry({"id": "0000-0000-0000-0000"}, errors=["boom"])

    writer.write_many([broken])

    assert captured["rows"] == []
    assert captured["actions"] == []


def test_write_delegates_to_write_many(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch)

    entry = writer.write(StreamEntry(ENTRY))

    assert entry.entry == ENTRY
    assert len(captured["rows"]) == 1


def test_fetching_missing_affiliations_can_be_disabled(monkeypatch):
    writer, captured = _capturing_writer(monkeypatch, fetch_missing_affiliations=False)

    writer.write_many([StreamEntry(ENTRY)])

    assert captured["fetch_missing"] is False

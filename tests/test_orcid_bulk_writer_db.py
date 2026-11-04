# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""The bulk writer must produce exactly what the names service and indexer produce."""

from __future__ import annotations

import copy

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from invenio_vocabularies.contrib.names.api import Name
from invenio_vocabularies.datastreams.datastreams import StreamEntry

from oarepo_vocabularies.orcid.writers import NamesBulkWriter

ORCID = "0000-0002-1825-0097"
SERVICE_ORCID = "0000-0001-5109-3700"


def _entry(orcid: str, **overrides) -> dict:
    """Return an entry as produced by the stock ORCID transformer."""
    return {
        "id": orcid,
        "given_name": "Josiah",
        "family_name": "Carberry",
        "identifiers": [{"scheme": "orcid", "identifier": orcid}],
        "affiliations": [
            {"name": "Brown University", "id": "05gq02987"},
            {"name": "Unknown Org", "id": "000000000"},
            {"name": "Wesleyan"},
        ],
        **overrides,
    }


def _without(data: dict, *keys: str) -> dict:
    return {key: value for key, value in data.items() if key not in keys}


@pytest.fixture
def names_service(app):
    return current_service_registry.get("names")


@pytest.fixture
def brown(app, db, search_clear):
    """Create the only affiliation of the vocabulary."""
    return current_service_registry.get("affiliations").create(
        system_identity,
        {
            "id": "05gq02987",
            "name": "Brown University",
            "acronym": "BU",
            "title": {"en": "Brown University"},
            "identifiers": [{"scheme": "ror", "identifier": "05gq02987"}],
        },
    )


def _index_document(record: Name) -> dict:
    return current_search_client.get(index=build_alias_name(Name.index._name), id=str(record.id))


def test_bulk_written_record_matches_the_service(app, db, brown, names_service):
    NamesBulkWriter(fetch_missing_affiliations=False).write_many([StreamEntry(_entry(ORCID))])
    # the same person created through the service; the unknown affiliation id would be
    # rejected by the service, so it gets the name only, as the writer does
    service_entry = _entry(SERVICE_ORCID)
    service_entry["affiliations"][1] = {"name": "Unknown Org"}
    names_service.create(system_identity, service_entry)
    Name.index.refresh()

    bulk = Name.pid.resolve(ORCID)
    reference = Name.pid.resolve(SERVICE_ORCID)

    # database json: the same as stored by the service (apart from the ids)
    def normalized(record: Name) -> dict:
        data = copy.deepcopy(dict(record))
        data["identifiers"] = sorted(i["scheme"] for i in data["identifiers"])
        return data

    assert normalized(bulk) == normalized(reference)
    assert bulk["affiliations"] == [{"id": "05gq02987"}, {"name": "Unknown Org"}, {"name": "Wesleyan"}]

    # index document: the same as Invenio's search dumper produces
    document = _index_document(bulk)
    assert document["_index"].startswith(build_alias_name(Name.index._name))
    assert document["_version"] == bulk.revision_id
    assert _without(document["_source"], "indexed_at") == _without(bulk.dumps(), "indexed_at")

    # the record can be read, searched and re-indexed through Invenio
    read = names_service.read(system_identity, ORCID).to_dict()
    assert read["name"] == "Carberry, Josiah"
    assert read["affiliations"][0] == {"id": "05gq02987", "name": "Brown University", "acronym": "BU"}
    hits = names_service.search(system_identity, params={"q": f'id:"{ORCID}"'}).to_dict()["hits"]
    assert hits["total"] == 1
    assert hits["hits"][0]["name"] == "Carberry, Josiah"
    names_service.indexer.index(bulk)


def test_existing_records_are_skipped_without_update(app, db, brown, names_service):
    NamesBulkWriter(fetch_missing_affiliations=False).write_many([StreamEntry(_entry(ORCID))])
    entry = StreamEntry(_entry(ORCID, given_name="Changed"))

    NamesBulkWriter(fetch_missing_affiliations=False).write_many([entry])
    Name.index.refresh()

    assert entry.op_type is None
    assert Name.pid.resolve(ORCID)["given_name"] == "Josiah"
    assert _index_document(Name.pid.resolve(ORCID))["_source"]["given_name"] == "Josiah"


def test_update_bumps_the_version_and_reindexes(app, db, brown, names_service):
    NamesBulkWriter(fetch_missing_affiliations=False).write_many([StreamEntry(_entry(ORCID))])
    entry = StreamEntry(_entry(ORCID, given_name="J."))

    NamesBulkWriter(update=True, fetch_missing_affiliations=False).write_many([entry])
    Name.index.refresh()

    record = Name.pid.resolve(ORCID)
    document = _index_document(record)
    assert entry.op_type == "update"
    assert record.model.version_id == 2
    assert record["name"] == "Carberry, J."
    assert document["_version"] == record.revision_id
    assert _without(document["_source"], "indexed_at") == _without(record.dumps(), "indexed_at")

    # a later update through the service still works on the bulk-written record
    data = _without(names_service.read(system_identity, ORCID).to_dict(), "links", "revision_id", "created", "updated")
    names_service.update(system_identity, ORCID, {**data, "given_name": "Josiah S."})
    assert names_service.read(system_identity, ORCID).to_dict()["name"] == "Carberry, Josiah S."


def test_no_transaction_is_open_while_calling_ror(app, db, brown, monkeypatch):
    """Holding a connection while waiting for ROR starves the worker's connection pool."""
    from oarepo_vocabularies.orcid import affiliations as aff_module

    monkeypatch.setattr(aff_module, "_state", aff_module._RorState())
    in_transaction_during_request: list[bool] = []

    class _Response:
        status_code = 404
        ok = False

        def __init__(self) -> None:
            self.headers: dict = {}

    class _Session:
        def __init__(self) -> None:
            self.headers: dict = {}

        def get(self, url, timeout):
            in_transaction_during_request.append(db.session().in_transaction())
            return _Response()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(aff_module.requests, "Session", _Session)

    NamesBulkWriter().write_many([StreamEntry(_entry(ORCID))])

    # the unknown affiliation was looked up in ROR, without holding a connection
    assert in_transaction_during_request == [False]
    assert Name.pid.resolve(ORCID)["affiliations"][1] == {"name": "Unknown Org"}


def test_no_transaction_is_open_while_waiting_for_the_rate_limit(app, db, brown, monkeypatch):
    """A thread waiting for ROR's rate limit must not hold a database connection."""
    from oarepo_vocabularies.orcid import affiliations as aff_module

    monkeypatch.setattr(aff_module, "_state", aff_module._RorState())
    in_transaction_while_sleeping: list[bool] = []

    def fake_sleep(seconds):
        in_transaction_while_sleeping.append(db.session().in_transaction())
        aff_module._state.backoff_until = 0.0  # the wait is over

    class _Response:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code
            self.ok = status_code < 400
            self.headers = {"Retry-After": "5"}

    class _Session:
        def __init__(self) -> None:
            self.headers: dict = {}
            self.responses = [_Response(429), _Response(429), _Response(404)]

        def get(self, url, timeout):
            # touch the database between the attempts, as a careless change might
            db.session.execute(db.text("select 1"))
            return self.responses.pop(0)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(aff_module, "_sleep", fake_sleep)
    monkeypatch.setattr(aff_module.requests, "Session", _Session)

    NamesBulkWriter().write_many([StreamEntry(_entry(ORCID))])

    # waited twice (two 429 answers), never inside a transaction
    assert in_transaction_while_sleeping == [False, False]

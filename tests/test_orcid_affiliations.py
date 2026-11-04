# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Unit tests for importing missing ROR affiliations (no database, no network)."""

from __future__ import annotations

import pytest
from flask import Flask

from oarepo_vocabularies.orcid import affiliations as aff_module
from oarepo_vocabularies.orcid.affiliations import AffiliationRef, import_from_ror, resolve_affiliations

ROR_ORG = {
    "id": "https://ror.org/05gq02987",
    "names": [
        {"lang": "en", "types": ["ror_display", "label"], "value": "Brown University"},
        {"lang": None, "types": ["acronym"], "value": "BU"},
    ],
    "locations": [{"geonames_details": {"country_code": "US", "country_name": "United States", "name": "Providence"}}],
    "types": ["education"],
    "status": "active",
    "external_ids": [],
}


class _Response:
    def __init__(self, status_code: int, payload: dict | None = None, headers: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}
        self.ok = status_code < 400

    def json(self) -> dict:
        return self._payload


class _Session:
    """Answer from ``responses``; a list is consumed one response per request."""

    def __init__(self, responses: dict[str, _Response | list[_Response]]) -> None:
        self.responses = responses
        self.headers: dict = {}
        self.requested: list[str] = []

    def get(self, url: str, timeout: int) -> _Response:
        ror_id = url.rsplit("/", 1)[-1]
        self.requested.append(ror_id)
        response = self.responses.get(ror_id, _Response(404))
        if isinstance(response, list):
            return response.pop(0) if len(response) > 1 else response[0]
        return response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["VOCABULARIES_AFFILIATION_SCHEMES"] = {"ror": {}}
    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def fresh_state(monkeypatch):
    monkeypatch.setattr(aff_module, "_state", aff_module._RorState())


@pytest.fixture(autouse=True)
def released(monkeypatch):
    """Record the releases of the database connection (there is no database here)."""
    released: list[int] = []
    monkeypatch.setattr(aff_module, "_release_connection", lambda: released.append(1))
    return released


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Record the waits instead of sleeping; after a wait the rate limit is over."""
    sleeps: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)
        aff_module._state.backoff_until = 0.0

    monkeypatch.setattr(aff_module, "_sleep", fake_sleep)
    return sleeps


@pytest.fixture
def created(monkeypatch):
    """Capture the affiliations created through the (mocked) service."""
    created: list[dict] = []
    monkeypatch.setattr(
        aff_module,
        "_create_affiliation",
        lambda ror_id, organization: created.append(organization) or True,
    )
    return created


def _use_session(monkeypatch, session: _Session) -> None:
    monkeypatch.setattr(aff_module.requests, "Session", lambda: session)


def test_imports_missing_organizations(app, monkeypatch, created):
    session = _Session({"05gq02987": _Response(200, ROR_ORG)})
    _use_session(monkeypatch, session)

    assert import_from_ror({"05gq02987"}) == {"05gq02987"}
    assert created == [ROR_ORG]


def test_sends_the_client_id(app, monkeypatch, created):
    app.config["OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID"] = "secret-client"
    session = _Session({"05gq02987": _Response(200, ROR_ORG)})
    _use_session(monkeypatch, session)

    import_from_ror({"05gq02987"})

    assert session.headers["Client-Id"] == "secret-client"


def test_fetches_every_missing_organization(app, monkeypatch, created):
    ids = {f"id{i:03d}" for i in range(500)}
    session = _Session(dict.fromkeys(ids, _Response(200, ROR_ORG)))
    _use_session(monkeypatch, session)

    assert import_from_ror(ids) == ids
    assert len(session.requested) == 500


def test_remembers_unknown_ids(app, monkeypatch, created):
    session = _Session({})
    _use_session(monkeypatch, session)

    import_from_ror({"nonexistent"})
    import_from_ror({"nonexistent"})

    assert session.requested == ["nonexistent"]


def test_waits_and_retries_after_a_rate_limit(app, monkeypatch, created, sleeps):
    session = _Session(
        {
            "a": [_Response(429, headers={"Retry-After": "30"}), _Response(200, ROR_ORG)],
            "b": _Response(200, ROR_ORG),
        }
    )
    _use_session(monkeypatch, session)

    assert import_from_ror({"a", "b"}) == {"a", "b"}
    assert session.requested == ["a", "a", "b"]
    # waited before the retry, roughly for the announced time
    assert len(sleeps) == 1
    assert 29 < sleeps[0] <= 30


def test_waits_the_default_time_without_retry_after(app, monkeypatch, created, sleeps):
    session = _Session({"a": [_Response(429), _Response(200, ROR_ORG)]})
    _use_session(monkeypatch, session)

    assert import_from_ror({"a"}) == {"a"}
    assert aff_module.RATE_LIMIT_BACKOFF - 1 < sleeps[0] <= aff_module.RATE_LIMIT_BACKOFF


def test_gives_up_after_repeated_rate_limits(app, monkeypatch, created, sleeps):
    session = _Session({"a": [_Response(429)], "b": _Response(200, ROR_ORG)})
    _use_session(monkeypatch, session)

    # "a" is kept as a name only, the rest of the batch is still fetched
    assert import_from_ror({"a", "b"}) == {"b"}
    assert session.requested.count("a") == aff_module.MAX_RATE_LIMIT_RETRIES


def test_resolve_reads_back_imported_ids(app, monkeypatch):
    ref = AffiliationRef(pid="05gq02987", uuid="u", version_id=1, name="Brown University", acronym="BU")
    database: dict[str, AffiliationRef] = {}

    def fake_load(ids):
        return {pid: database[pid] for pid in ids if pid in database}

    def fake_import(ids):
        database[ref.pid] = ref
        return {ref.pid}

    monkeypatch.setattr(aff_module, "load_affiliations", fake_load)
    monkeypatch.setattr(aff_module, "import_from_ror", fake_import)

    assert resolve_affiliations({"05gq02987", "missing"}) == {"05gq02987": ref}


def test_resolve_does_not_fetch_when_disabled(app, monkeypatch):
    monkeypatch.setattr(aff_module, "load_affiliations", lambda ids: {})
    monkeypatch.setattr(aff_module, "import_from_ror", lambda ids: pytest.fail("must not fetch"))

    assert resolve_affiliations({"x"}, fetch_missing=False) == {}


def test_create_affiliation_transforms_the_ror_record(app, monkeypatch):
    calls: list[dict] = []

    class _Service:
        def create(self, identity, data):
            calls.append(data)

    class _Registry:
        def get(self, name):
            assert name == "affiliations"
            return _Service()

    monkeypatch.setattr("invenio_records_resources.proxies.current_service_registry", _Registry())

    assert aff_module._create_affiliation("05gq02987", ROR_ORG) is True
    assert calls[0]["id"] == "05gq02987"
    assert calls[0]["name"] == "Brown University"
    assert calls[0]["acronym"] == "BU"


def test_create_affiliation_tolerates_a_concurrent_create(app, monkeypatch):
    class _Service:
        def create(self, identity, data):
            raise RuntimeError("PID already exists")

    class _Registry:
        def get(self, name):
            return _Service()

    monkeypatch.setattr("invenio_records_resources.proxies.current_service_registry", _Registry())
    monkeypatch.setattr(aff_module.db.session, "rollback", lambda: None, raising=False)
    monkeypatch.setattr(
        aff_module,
        "load_affiliations",
        lambda ids: {"05gq02987": AffiliationRef("05gq02987", "u", 1, "Brown University", None)},
    )

    assert aff_module._create_affiliation("05gq02987", ROR_ORG) is True


def test_unknown_ids_are_asked_again_after_the_ttl(app, monkeypatch, created):
    clock = [0.0]
    monkeypatch.setattr(aff_module, "_state", aff_module._RorState(timer=lambda: clock[0]))
    session = _Session({})
    _use_session(monkeypatch, session)

    import_from_ror({"nonexistent"})
    clock[0] = aff_module.NOT_FOUND_TTL - 1
    import_from_ror({"nonexistent"})
    assert session.requested == ["nonexistent"]

    # an id may be registered in ROR later: after the ttl it is fetched again
    clock[0] = aff_module.NOT_FOUND_TTL + 1
    import_from_ror({"nonexistent"})
    assert session.requested == ["nonexistent", "nonexistent"]


def test_the_memory_of_unknown_ids_is_bounded():
    state = aff_module._RorState(not_found_maxsize=3)

    for ror_id in ("a", "b", "c", "d", "e"):
        state.mark_not_found(ror_id)

    assert len(state.not_found) == 3
    assert not state.is_not_found("a")
    assert state.is_not_found("e")


def test_releases_the_database_connection_before_every_request(app, monkeypatch, created, released):
    session = _Session({"a": _Response(200, ROR_ORG), "b": _Response(404)})
    original_get = session.get

    def get(url, timeout):
        # the release must happen before the request, not after it
        assert len(released) == len(session.requested) + 1
        return original_get(url, timeout)

    session.get = get
    _use_session(monkeypatch, session)

    import_from_ror({"a", "b"})

    assert len(released) == 2

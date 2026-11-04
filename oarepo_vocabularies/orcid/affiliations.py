# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Resolution of the ROR affiliations referenced by ORCID name records.

A name record may only reference an affiliation by ``id`` if that id exists in the
``affiliations`` vocabulary: Invenio dereferences the id whenever the record is read or
indexed and fails if it does not exist. The bulk writer therefore resolves all the ids of a
batch with a single query, tries to import the missing ones from the ROR API, and keeps only
the name of an affiliation that still can not be resolved.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import requests
from cachetools import TTLCache
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db

from oarepo_vocabularies.orcid.urls import sanitize_url

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from invenio_records_resources.services import RecordService

log = logging.getLogger(__name__)

CONFIG_ROR_API_URL = "OAREPO_VOCABULARIES_ORCID_ROR_API_URL"
CONFIG_ROR_CLIENT_ID = "OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID"

DEFAULT_ROR_API_URL = "https://api.ror.org/v2"
ROR_TIMEOUT = 30
RATE_LIMIT_BACKOFF = 60
"""Seconds to wait after the ROR API answered 429 without ``Retry-After``."""
MAX_RATE_LIMIT_RETRIES = 10
"""Rate-limited attempts per organization before it is given up (kept as a name only)."""
NOT_FOUND_TTL = 12 * 60 * 60
"""Seconds an id unknown to ROR is not asked for again."""
NOT_FOUND_MAXSIZE = 100_000
"""Maximum number of remembered unknown ids (least recently used are dropped first)."""


@dataclass(frozen=True)
class AffiliationRef:
    """An affiliation as Invenio dereferences it into a name record."""

    pid: str
    uuid: str
    version_id: int
    name: str | None
    acronym: str | None

    def dereferenced(self) -> dict[str, Any]:
        """Return the affiliation as dumped by ``PIDListRelation(keys=["name", "acronym"])``."""
        result: dict[str, Any] = {"id": self.pid}
        if self.name is not None:
            result["name"] = self.name
        if self.acronym is not None:
            result["acronym"] = self.acronym
        # the relation version marker uses the revision id, which is version_id - 1
        result["@v"] = f"{self.uuid}::{self.version_id - 1}"
        return result


class _RorState:
    """Process-wide memory of ids ROR does not know and of the rate limit.

    Lives as long as the worker, so the memory of unknown ids is bounded in size and
    expires: an id may be registered in ROR later, and a worker can run for weeks.
    """

    def __init__(
        self,
        not_found_maxsize: int = NOT_FOUND_MAXSIZE,
        not_found_ttl: float = NOT_FOUND_TTL,
        timer: Callable[[], float] = time.monotonic,
    ) -> None:
        self.lock = threading.Lock()  # TTLCache is not thread safe
        self.not_found: TTLCache[str, bool] = TTLCache(maxsize=not_found_maxsize, ttl=not_found_ttl, timer=timer)
        self.backoff_until = 0.0

    def is_not_found(self, ror_id: str) -> bool:
        with self.lock:
            return ror_id in self.not_found

    def mark_not_found(self, ror_id: str) -> None:
        with self.lock:
            self.not_found[ror_id] = True


_state = _RorState()


def _affiliation_api() -> Any:
    from invenio_vocabularies.contrib.affiliations.api import Affiliation

    return Affiliation


def load_affiliations(ids: Iterable[str]) -> dict[str, AffiliationRef]:
    """Return the affiliations of the vocabulary with the given ids, in one query."""
    ids = set(ids)
    if not ids:
        return {}
    model = _affiliation_api().model_cls
    rows = db.session.execute(
        db.select(model.pid, model.id, model.version_id, model.json).where(model.pid.in_(ids))
    ).all()
    return {
        pid: AffiliationRef(
            pid=pid,
            uuid=str(uuid),
            version_id=version_id,
            name=(data or {}).get("name"),
            acronym=(data or {}).get("acronym"),
        )
        for pid, uuid, version_id, data in rows
    }


def resolve_affiliations(ids: Iterable[str], *, fetch_missing: bool = True) -> dict[str, AffiliationRef]:
    """Resolve ROR ids against the vocabulary, importing missing ones from the ROR API."""
    ids = set(ids)
    known = load_affiliations(ids)
    missing = ids - known.keys()
    if missing and fetch_missing:
        imported = import_from_ror(missing)
        if imported:
            # read them back: this also picks up ids created concurrently by another task
            known.update(load_affiliations(imported))
    return known


def _release_connection() -> None:
    """End the current transaction so that its connection goes back to the pool.

    Must be called before any network call or wait: a session keeps its connection checked
    out ("idle in transaction") until the transaction ends. Holding it while waiting for
    ROR starves the pool (``QueuePool limit ... reached``) for every other task in the worker.
    Only reads happen before this point, so committing does not persist anything unexpected.
    """
    db.session.commit()


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _wait_for_rate_limit() -> None:
    """Wait until the rate limit announced by ROR is over (shared by all threads).

    The database connection is released before sleeping, so that a waiting thread never
    holds a connection the other tasks of the worker need.
    """
    delay = _state.backoff_until - time.monotonic()
    if delay > 0:
        _release_connection()
        _sleep(delay)


def _set_backoff(response: requests.Response) -> float:
    """Remember the rate limit announced by a 429 response; return the delay."""
    try:
        delay = max(float(response.headers.get("Retry-After", RATE_LIMIT_BACKOFF)), 1.0)
    except ValueError:
        delay = RATE_LIMIT_BACKOFF
    with _state.lock:
        _state.backoff_until = max(_state.backoff_until, time.monotonic() + delay)
    return delay


def import_from_ror(ror_ids: Iterable[str]) -> set[str]:
    """Import ROR organizations into the affiliations vocabulary.

    Every organization is fetched; when ROR rate-limits the requests, the import waits and
    retries. Returns the ids that are now present (imported here or concurrently).
    """
    candidates = sorted(ror_id for ror_id in set(ror_ids) if not _state.is_not_found(ror_id))
    if not candidates:
        return set()

    api_url = sanitize_url(str(current_app.config.get(CONFIG_ROR_API_URL) or DEFAULT_ROR_API_URL))
    headers = {"Accept": "application/json"}
    client_id = current_app.config.get(CONFIG_ROR_CLIENT_ID)
    if client_id:
        headers["Client-Id"] = str(client_id)

    imported: set[str] = set()
    with requests.Session() as session:
        session.headers.update(headers)
        for ror_id in candidates:
            organization = _fetch(session, api_url, ror_id)
            if organization is not None and _create_affiliation(ror_id, organization):
                imported.add(ror_id)
    if imported:
        log.info("Imported %s affiliations from ROR", len(imported))
    return imported


def _fetch(session: requests.Session, api_url: str, ror_id: str) -> dict[str, Any] | None:
    """Fetch a single ROR organization, ``None`` if it can not be used."""
    _release_connection()
    for attempt in range(1, MAX_RATE_LIMIT_RETRIES + 1):
        _wait_for_rate_limit()
        try:
            response = session.get(f"{api_url}/organizations/{ror_id}", timeout=ROR_TIMEOUT)
        except requests.RequestException as exc:
            log.warning("Could not fetch ROR organization %s: %s", ror_id, exc)
            return None
        if response.status_code != 429:  # noqa: PLR2004
            break
        delay = _set_backoff(response)
        log.warning(
            "ROR API rate limit hit, retrying %s in %.0f s (attempt %s of %s)",
            ror_id,
            delay,
            attempt,
            MAX_RATE_LIMIT_RETRIES,
        )
    else:
        log.warning("Giving up on ROR organization %s, still rate limited", ror_id)
        return None
    if response.status_code in (400, 404):
        _state.mark_not_found(ror_id)
        return None
    if not response.ok:
        log.warning("ROR API returned %s for %s", response.status_code, ror_id)
        return None
    return dict(response.json())


def _create_affiliation(ror_id: str, organization: dict[str, Any]) -> bool:
    """Create the affiliation through the service; ``True`` if it exists afterwards."""
    from invenio_records_resources.proxies import current_service_registry
    from invenio_vocabularies.contrib.affiliations.datastreams import (
        AffiliationsRORTransformer,
    )
    from invenio_vocabularies.datastreams import StreamEntry

    try:
        entry = AffiliationsRORTransformer().apply(StreamEntry(organization)).entry
    except Exception as exc:  # noqa: BLE001 - a malformed organization must not stop the batch
        log.warning("Could not transform ROR organization %s: %s", ror_id, exc)
        return False
    if entry.get("id") != ror_id:
        log.warning("ROR returned %s when asked for %s, not importing it", entry.get("id"), ror_id)
        return False

    try:
        service = cast("RecordService[Any]", current_service_registry.get("affiliations"))
        service.create(system_identity, entry)
    except Exception as exc:  # noqa: BLE001 - e.g. created meanwhile by a concurrent batch
        db.session.rollback()
        exists = ror_id in load_affiliations([ror_id])
        if not exists:
            log.warning("Could not create affiliation %s: %s", ror_id, exc)
        return exists
    return True


__all__ = ["AffiliationRef", "import_from_ror", "load_affiliations", "resolve_affiliations"]

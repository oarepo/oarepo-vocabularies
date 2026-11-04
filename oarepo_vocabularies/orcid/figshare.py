# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Discovery of the ORCID public data file published on Figshare.

ORCID releases a snapshot of all public registry data once a year and publishes it in
the ORCID Figshare group. The public API exposes both the group listing and the per
article file metadata, so the newest file can be found without any human interaction.

The "ORCID Annual Public Data Files" collection is consulted first, but it lags behind
the actual release: the 2026 file was published on 2026-10-22 and was still missing from
the collection weeks later. A group search is therefore used as well.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import requests
from flask import current_app, has_app_context

from oarepo_vocabularies.orcid.urls import sanitize_url

if TYPE_CHECKING:
    from collections.abc import Mapping

DEFAULT_COLLECTION_ID = 7931102
"""Figshare collection id of "ORCID Annual Public Data Files"."""

DEFAULT_GROUP_ID = 8907
"""Figshare group id of ORCID; holds the data files even before they join the collection."""

DEFAULT_API_URL = "https://api.figshare.com/v2"
"""Base url of the public Figshare API."""

DEFAULT_TIMEOUT = 60
"""Timeout in seconds used for the Figshare requests."""

SUMMARIES_SUFFIX = "_summaries.tar.gz"
"""Only the summaries archive is needed to build name records."""

CONFIG_COLLECTION_ID = "OAREPO_VOCABULARIES_ORCID_DUMP_COLLECTION_ID"
CONFIG_GROUP_ID = "OAREPO_VOCABULARIES_ORCID_DUMP_GROUP_ID"
CONFIG_API_URL = "OAREPO_VOCABULARIES_ORCID_DUMP_API_URL"
CONFIG_YEAR = "OAREPO_VOCABULARIES_ORCID_DUMP_YEAR"

_PAGE_SIZE = 100
_DATA_FILE_TITLE_RE = re.compile(r"ORCID\s+Public\s+Data\s?File\s+(20\d{2})", re.IGNORECASE)
_YEAR_RE = re.compile(r"\b(20\d{2})\b")


class OrcidDumpError(RuntimeError):
    """Raised when the ORCID public data file can not be resolved."""


@dataclass(frozen=True)
class OrcidDump:
    """A resolved ORCID public data file."""

    year: int
    """Release year of the data file."""

    name: str
    """File name of the summaries archive."""

    download_url: str
    """Direct download url of the summaries archive."""

    size: int
    """Size of the compressed archive in bytes."""

    md5: str | None
    """Checksum reported by Figshare (``supplied_md5``), if any."""

    article_id: int
    """Figshare article id the archive belongs to."""


def _logger() -> Any:
    """Return the application logger when there is an application context."""
    if has_app_context():
        return current_app.logger
    return logging.getLogger(__name__)


def _config(key: str) -> Any:
    """Read a configuration value, tolerating the absence of an application context."""
    if has_app_context():
        return current_app.config.get(key)
    return None


def is_public_data_file(article: Mapping[str, Any]) -> bool:
    """Return whether the article is an ORCID public data file of a given year.

    The ORCID group also contains annual reports and iD icon sets, whose titles contain a
    year as well, so the title has to be matched explicitly. Note the inconsistent
    spelling across releases: "Public Data File 2026" but "Public DataFile 2014".
    """
    return bool(_DATA_FILE_TITLE_RE.search(str(article.get("title", ""))))


def year_of(article: Mapping[str, Any]) -> int:
    """Extract the release year from a Figshare article title.

    The year has to be read from the title: ``published_date`` only reflects when a
    file was (re-)uploaded, so a corrected 2022 archive can be "published" after the
    2024 one. Returns ``0`` when the title does not contain a year.
    """
    match = _YEAR_RE.search(str(article.get("title", "")))
    return int(match.group(1)) if match else 0


def collection_articles(
    collection_id: int = DEFAULT_COLLECTION_ID,
    api_url: str = DEFAULT_API_URL,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    """Return every article of an ORCID public data file collection.

    The Figshare endpoint is paginated with only 10 items per page by default while
    the collection holds more than that, so the page size is raised explicitly.
    """
    http = session or requests
    response = http.get(
        f"{sanitize_url(api_url)}/collections/{collection_id}/articles",
        params={"page_size": _PAGE_SIZE},
        timeout=timeout,
    )
    response.raise_for_status()
    return list(response.json())


def group_articles(
    group_id: int = DEFAULT_GROUP_ID,
    api_url: str = DEFAULT_API_URL,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    """Return the data files published by the ORCID Figshare group, newest first.

    A freshly released file is published in the group first and only added to the
    collection later (or not at all, as happened with the 2026 release).
    """
    http = session or requests
    response = http.post(
        f"{sanitize_url(api_url)}/articles/search",
        json={
            "group": group_id,
            "page_size": _PAGE_SIZE,
            "order": "published_date",
            "order_direction": "desc",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return [article for article in response.json() if is_public_data_file(article)]


def article_metadata(
    article: Mapping[str, Any],
    api_url: str = DEFAULT_API_URL,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Return the metadata of a single Figshare article, including its files."""
    http = session or requests
    url = article.get("url") or f"{api_url}/articles/{article['id']}"
    response = http.get(sanitize_url(url), timeout=timeout)
    response.raise_for_status()
    return dict(response.json())


def _all_articles(
    *,
    collection_id: int,
    group_id: int,
    api_url: str,
    session: requests.Session | None,
    timeout: int,
) -> list[dict[str, Any]]:
    """Collect the candidate articles from the collection and the group, de-duplicated."""
    articles = collection_articles(collection_id=collection_id, api_url=api_url, session=session, timeout=timeout)
    try:
        articles += group_articles(group_id=group_id, api_url=api_url, session=session, timeout=timeout)
    except (requests.RequestException, ValueError) as exc:
        # the collection alone is still usable, it just may be a release behind
        _logger().warning("Could not list the ORCID Figshare group, falling back to the collection: %s", exc)

    unique: dict[Any, dict[str, Any]] = {}
    for article in articles:
        if is_public_data_file(article):
            unique.setdefault(article["id"], article)
    return list(unique.values())


def resolve_dump(  # noqa: PLR0913 — the keyword arguments mirror the configuration keys
    year: int | None = None,
    *,
    collection_id: int | None = None,
    group_id: int | None = None,
    api_url: str | None = None,
    session: requests.Session | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> OrcidDump:
    """Resolve the ORCID public data file that should be imported.

    :param year: an explicit release year. ``None`` uses
        :data:`CONFIG_YEAR`, which is pinned to a validated release so that a load is
        reproducible. When both are ``None`` the newest file available wins.
    """
    collection_id = int(collection_id or _config(CONFIG_COLLECTION_ID) or DEFAULT_COLLECTION_ID)
    group_id = int(group_id or _config(CONFIG_GROUP_ID) or DEFAULT_GROUP_ID)
    api_url = str(api_url or _config(CONFIG_API_URL) or DEFAULT_API_URL)

    if year is None:
        configured_year = _config(CONFIG_YEAR)
        year = int(configured_year) if configured_year is not None else None

    articles = _all_articles(
        collection_id=collection_id,
        group_id=group_id,
        api_url=api_url,
        session=session,
        timeout=timeout,
    )
    if not articles:
        raise OrcidDumpError(f"no ORCID public data file found in collection {collection_id} or group {group_id}")

    newest = max(articles, key=year_of)
    if year is None:
        chosen = newest
    else:
        chosen = next((article for article in articles if year_of(article) == year), None)
        if chosen is None:
            available = sorted({year_of(article) for article in articles})
            raise OrcidDumpError(f"no {year} public data file available, found years: {available}")
        if year_of(newest) > year_of(chosen):
            _logger().warning(
                "A newer ORCID public data file exists (%s) but the import is pinned to %s. Set %s to change that.",
                year_of(newest),
                year,
                CONFIG_YEAR,
            )

    metadata = article_metadata(chosen, api_url=api_url, session=session, timeout=timeout)
    files = metadata.get("files") or []
    summaries = [file for file in files if str(file.get("name", "")).endswith(SUMMARIES_SUFFIX)]
    if len(summaries) != 1:
        raise OrcidDumpError(
            f"expected exactly one {SUMMARIES_SUFFIX} in article {chosen.get('id')}, "
            f"found: {[file.get('name') for file in files]}"
        )

    summaries_file = summaries[0]
    download_url = summaries_file.get("download_url")
    if not download_url:
        raise OrcidDumpError(f"article {chosen.get('id')} has no download url for {summaries_file.get('name')}")

    return OrcidDump(
        year=year_of(chosen),
        name=str(summaries_file["name"]),
        download_url=sanitize_url(download_url),
        size=int(summaries_file.get("size") or 0),
        md5=summaries_file.get("supplied_md5") or None,
        article_id=int(chosen["id"]),
    )

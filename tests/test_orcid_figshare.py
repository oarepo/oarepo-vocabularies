# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for the Figshare discovery of the ORCID public data file."""

from __future__ import annotations

import logging

import pytest
import requests

from oarepo_vocabularies.orcid import figshare
from oarepo_vocabularies.orcid.figshare import OrcidDumpError, resolve_dump, year_of

API = figshare.DEFAULT_API_URL
COLLECTION_URL = f"{API}/collections/{figshare.DEFAULT_COLLECTION_ID}/articles"
GROUP_SEARCH_URL = f"{API}/articles/search"


class _Response:
    """Minimal stand-in for a requests response."""

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        """Pretend the request succeeded."""

    def json(self):
        return self._payload


class _Session:
    """Minimal stand-in for a requests session."""

    def __init__(self, responses):
        self._responses = responses
        self.calls = []
        self.post_fails = False

    def get(self, url, params=None, timeout=None):
        self.calls.append(("GET", url, params))
        return _Response(self._responses[url])

    def post(self, url, json=None, timeout=None):
        self.calls.append(("POST", url, json))
        if self.post_fails:
            raise requests.RequestException("group search unavailable")
        return _Response(self._responses.get(("POST", url), []))


def _article(article_id: int, year: int, published: str) -> dict:
    return {
        "id": article_id,
        "title": f"ORCID Public Data File {year}",
        "published_date": published,
        "url": f"{figshare.DEFAULT_API_URL}/articles/{article_id}",
    }


# 2022 was re-published in August 2025, so ordering by published_date would pick it
# over the 2025 file released in October 2025.
ARTICLES = [
    _article(30375589, 2025, "2025-10-20T13:38:32Z"),
    _article(21220892, 2022, "2025-08-19T13:43:28Z"),
    _article(8340689, 2014, "2025-07-16T15:29:40Z"),
]


def _article_payload(article_id: int, names: list[str]) -> dict:
    return {
        "id": article_id,
        "files": [
            {
                "name": name,
                "size": 46_328_319_190,
                "download_url": f"https://ndownloader.example/files/{article_id}/{name}",
                "supplied_md5": "210edf71f4a2bb44dd33aaa3037b3f17",
                "computed_md5": "",
            }
            for name in names
        ],
    }


RESPONSES = {
    COLLECTION_URL: ARTICLES,
    f"{figshare.DEFAULT_API_URL}/articles/30375589": _article_payload(
        30375589, ["ORCID_2025_10_summaries.tar.gz", "ORCID_2025_10_activities_0.tar.gz"]
    ),
    f"{figshare.DEFAULT_API_URL}/articles/21220892": _article_payload(21220892, ["ORCID_2022_10_summaries.tar.gz"]),
    f"{figshare.DEFAULT_API_URL}/articles/8340689": _article_payload(8340689, ["ORCID_2014_10_summaries.tar.gz"]),
}

# the 2026 release exists in the ORCID Figshare group but was not added to the collection
DATA_FILE_2026 = _article(34697766, 2026, "2026-10-22T08:03:59Z")
ANNUAL_REPORT = {
    "id": 31846192,
    "title": "ORCID 2025 Annual Report",
    "published_date": "2026-04-01T00:00:00Z",
    "url": f"{figshare.DEFAULT_API_URL}/articles/31846192",
}
RESPONSES_WITH_2026 = {
    **RESPONSES,
    ("POST", GROUP_SEARCH_URL): [DATA_FILE_2026, ANNUAL_REPORT],
    f"{figshare.DEFAULT_API_URL}/articles/34697766": _article_payload(
        34697766, ["ORCID_2026_10_summaries.tar.gz", "ORCID_2026_10_activities_0.tar.gz"]
    ),
}


def test_year_of_reads_the_title():
    assert year_of({"title": "ORCID Public Data File 2025"}) == 2025
    assert year_of({"title": "no year here"}) == 0


def test_only_data_file_titles_are_accepted():
    # the group also holds annual reports and icon sets, whose titles contain a year
    assert figshare.is_public_data_file({"title": "ORCID Public Data File 2026"})
    assert figshare.is_public_data_file({"title": "ORCID Public DataFile 2014"})
    assert not figshare.is_public_data_file({"title": "ORCID 2025 Annual Report"})


def test_collection_articles_raises_the_page_size():
    session = _Session(RESPONSES)

    articles = figshare.collection_articles(session=session)

    assert len(articles) == 3
    method, url, params = session.calls[0]
    assert (method, url) == ("GET", COLLECTION_URL)
    # the endpoint returns 10 items by default and the collection has more
    assert params == {"page_size": 100}


def test_resolve_uses_newest_title_year_not_published_date():
    session = _Session({**RESPONSES, COLLECTION_URL: ARTICLES})

    dump = resolve_dump(session=session)

    assert dump.year == 2025
    assert dump.article_id == 30375589
    assert dump.name == "ORCID_2025_10_summaries.tar.gz"
    assert dump.size == 46_328_319_190
    assert dump.md5 == "210edf71f4a2bb44dd33aaa3037b3f17"


def test_resolve_pins_the_requested_year():
    session = _Session(RESPONSES)

    dump = resolve_dump(2022, session=session)

    assert dump.year == 2022
    assert dump.name == "ORCID_2022_10_summaries.tar.gz"


def test_resolve_uses_the_configured_year_when_none_is_given(monkeypatch):
    monkeypatch.setattr(
        figshare,
        "_config",
        lambda key: 2014 if key == figshare.CONFIG_YEAR else None,
    )
    session = _Session(RESPONSES)

    dump = resolve_dump(session=session)

    assert dump.year == 2014


def test_resolve_warns_about_a_newer_file_but_keeps_the_pin(monkeypatch, caplog):
    monkeypatch.setattr(
        figshare,
        "_config",
        lambda key: 2022 if key == figshare.CONFIG_YEAR else None,
    )
    session = _Session(RESPONSES)

    with caplog.at_level(logging.WARNING):
        dump = resolve_dump(session=session)

    assert dump.year == 2022
    assert "A newer ORCID public data file exists (2025)" in caplog.text


def test_resolve_raises_for_an_unknown_year():
    session = _Session(RESPONSES)

    with pytest.raises(OrcidDumpError, match="no 2031 public data file"):
        resolve_dump(2031, session=session)


def test_resolve_requires_the_summaries_file():
    responses = {
        COLLECTION_URL: ARTICLES,
        f"{figshare.DEFAULT_API_URL}/articles/30375589": _article_payload(
            30375589, ["ORCID_2025_10_activities_0.tar.gz"]
        ),
    }
    session = _Session(responses)

    with pytest.raises(OrcidDumpError, match=r"expected exactly one _summaries\.tar\.gz"):
        resolve_dump(2025, session=session)


def test_group_search_finds_a_release_missing_from_the_collection():
    """The 2026 file was published in the group but never added to the collection."""
    session = _Session(RESPONSES_WITH_2026)

    dump = resolve_dump(2026, session=session)

    assert dump.year == 2026
    assert dump.article_id == 34697766
    assert dump.name == "ORCID_2026_10_summaries.tar.gz"


def test_newest_ignores_articles_that_are_not_data_files():
    session = _Session(RESPONSES_WITH_2026)

    # the annual report is the newest hit in the group, but it is not a data file
    dump = resolve_dump(session=session)

    assert dump.year == 2026


def test_articles_present_in_both_sources_are_deduplicated():
    session = _Session(RESPONSES_WITH_2026)

    articles = figshare._all_articles(
        collection_id=figshare.DEFAULT_COLLECTION_ID,
        group_id=figshare.DEFAULT_GROUP_ID,
        api_url=API,
        session=session,
        timeout=60,
    )

    ids = [article["id"] for article in articles]
    assert len(ids) == len(set(ids))
    assert 30375589 in ids
    assert 34697766 in ids
    assert ANNUAL_REPORT["id"] not in ids


def test_falls_back_to_the_collection_when_the_group_search_fails(caplog):
    session = _Session(RESPONSES)
    session.post_fails = True

    with caplog.at_level(logging.WARNING):
        dump = resolve_dump(2025, session=session)

    assert dump.year == 2025
    assert "falling back to the collection" in caplog.text

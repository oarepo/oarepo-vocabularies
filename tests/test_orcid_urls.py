# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for the url sanitization used before any outbound request."""

from __future__ import annotations

import pytest

from oarepo_vocabularies.orcid import figshare
from oarepo_vocabularies.orcid.figshare import resolve_dump
from oarepo_vocabularies.orcid.readers import HttpStreamReader
from oarepo_vocabularies.orcid.urls import UnsafeUrlError, sanitize_url

API = figshare.DEFAULT_API_URL
COLLECTION_URL = f"{API}/collections/{figshare.DEFAULT_COLLECTION_ID}/articles"


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        """Pretend the request succeeded."""

    def json(self):
        return self._payload


class _Session:
    """Records the urls it is asked to fetch, so a leaked url is visible in a test."""

    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(("GET", url))
        return _Response(self._responses[url])

    def post(self, url, json=None, timeout=None):
        self.calls.append(("POST", url))
        return _Response(self._responses.get(("POST", url), []))


@pytest.mark.parametrize(
    "url",
    [
        "https://api.figshare.com/v2",
        "https://ndownloader.figshare.com/files/70342863",
        "https://api.figshare.com/v2/articles/34697766?page=1#top",
        "HTTPS://api.figshare.com/v2",
    ],
)
def test_accepts_absolute_https_urls(url):
    assert sanitize_url(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://api.figshare.com/v2",
        "ftp://example.org/data.tar.gz",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "//example.org/data.tar.gz",
        "/relative/path",
        "https:///no-host",
        "",
        None,
        42,
        b"https://api.figshare.com/v2",
    ],
)
def test_rejects_everything_that_is_not_https(url):
    with pytest.raises(UnsafeUrlError):
        sanitize_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://user:secret@example.org/data.tar.gz",
        "https://user@example.org/data.tar.gz",
    ],
)
def test_rejects_urls_with_embedded_credentials(url):
    with pytest.raises(UnsafeUrlError, match="must not contain credentials"):
        sanitize_url(url)


def test_collection_listing_rejects_a_plain_http_api_url():
    session = _Session({})
    with pytest.raises(UnsafeUrlError):
        figshare.collection_articles(api_url="http://api.figshare.com/v2", session=session)
    assert session.calls == []


def test_group_search_rejects_a_plain_http_api_url():
    session = _Session({})
    with pytest.raises(UnsafeUrlError):
        figshare.group_articles(api_url="http://api.figshare.com/v2", session=session)
    assert session.calls == []


def test_article_metadata_rejects_a_url_from_the_api_response():
    session = _Session({})
    article = {"id": 1, "title": "ORCID Public Data File 2026", "url": "http://evil.example.org/a"}

    with pytest.raises(UnsafeUrlError):
        figshare.article_metadata(article, session=session)
    assert session.calls == []


def test_resolve_dump_rejects_an_insecure_download_url():
    article = {
        "id": 1,
        "title": "ORCID Public Data File 2026",
        "published_date": "2026-10-22T08:03:59Z",
        "url": f"{API}/articles/1",
    }
    responses = {
        COLLECTION_URL: [article],
        f"{API}/articles/1": {
            "id": 1,
            "files": [
                {
                    "name": "ORCID_2026_10_summaries.tar.gz",
                    "size": 1,
                    "download_url": "http://evil.example.org/summaries.tar.gz",
                    "supplied_md5": "abc",
                }
            ],
        },
    }
    session = _Session(responses)

    with pytest.raises(UnsafeUrlError):
        resolve_dump(2026, session=session)


def test_resolve_dump_returns_a_sanitized_download_url():
    article = {
        "id": 1,
        "title": "ORCID Public Data File 2026",
        "published_date": "2026-10-22T08:03:59Z",
        "url": f"{API}/articles/1",
    }
    download_url = "https://ndownloader.figshare.com/files/70342863"
    responses = {
        COLLECTION_URL: [article],
        f"{API}/articles/1": {
            "id": 1,
            "files": [
                {
                    "name": "ORCID_2026_10_summaries.tar.gz",
                    "size": 1,
                    "download_url": download_url,
                    "supplied_md5": "abc",
                }
            ],
        },
    }
    session = _Session(responses)

    dump = resolve_dump(2026, session=session)

    assert dump.download_url == download_url


def test_reader_refuses_to_open_a_non_https_url():
    reader = HttpStreamReader("http://example.org/summaries.tar.gz")

    # the url is validated before any connection is attempted
    with pytest.raises(UnsafeUrlError):
        next(iter(reader.read()))

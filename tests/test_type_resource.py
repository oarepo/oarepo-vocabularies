# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for vocabulary type resource."""

from __future__ import annotations


def test_resource_get(
    app,
    client,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
    clear_vocabulary_permissions,
):
    resp = client.get("/api/vocabularies/").json

    results = resp
    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0


def test_accept_header(
    app,
    client,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
    clear_vocabulary_permissions,
):
    resp = client.get("/api/vocabularies/").json

    results = resp
    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0


def test_ui_endpoint_without_slash(app, client, db, identity, vocab_cf, lang_data_many, fake_manifest):
    resp_1 = client.get("/vocabularies/")
    resp_2 = client.get("/vocabularies")

    assert resp_1.data == resp_2.data

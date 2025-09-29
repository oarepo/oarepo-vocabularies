#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_extra_cf(app, db, cache, lang_type, vocab_cf, search_clear):
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"


@pytest.mark.skip(reason="ICU sort later")
def test_czech_sort(app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear):
    data = client.get("/api/vocabularies/languages?sort=title", headers=[("Accept-Language", "cs")]).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina",
        "Angličtina (A pro řazení)",
        "Angličtina (UK)",
        "Angličtina (US)",
    ]


@pytest.mark.skip(reason="ICU sort later")
def test_oldest_sort(app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear):
    data = client.get("/api/vocabularies/languages?sort=oldest", headers=[("Accept-Language", "cs")]).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina",
        "Angličtina (US)",
        "Angličtina (UK)",
        "Angličtina (A pro řazení)",
    ]


@pytest.mark.skip(reason="ICU sort later")
def test_newest_sort(app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear):
    data = client.get("/api/vocabularies/languages?sort=newest", headers=[("Accept-Language", "cs")]).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina (A pro řazení)",
        "Angličtina (UK)",
        "Angličtina (US)",
        "Angličtina",
    ]


@pytest.mark.skip(reason="ICU sort later")
def test_czech_suggest(app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear):
    data = client.get(
        "/api/vocabularies/languages?suggest=%C5%99azen%C3%AD",
        headers=[("Accept-Language", "cs")],
    ).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina (A pro řazení)",
    ]

    data = client.get(
        "/api/vocabularies/languages?suggest=%C5%99az",
        headers=[("Accept-Language", "cs")],
    ).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina (A pro řazení)",
    ]


def test_ui_serializer(app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear):
    data = client.get(
        "/api/vocabularies/languages",
        headers=[
            ("Accept-Language", "cs"),
            ("Accept", "application/vnd.inveniordm.v1+json"),
        ],
    ).json

    assert data["hits"]["hits"][0]["ui"]["hierarchy"] == {
        "parent": "eng.UK",
        "ancestors": ["eng.UK", "eng"],
        "level": 3,
        "ancestors_or_self": ["eng.UK.S", "eng.UK", "eng"],
        "titles": ["Angličtina (A pro řazení)", "Angličtina (UK)", "Angličtina"],
        "leaf": True,
    }
    assert data["hits"]["hits"][0]["ui"]["title"] == "Angličtina (A pro řazení)"


def test_type_ui_serializer(app, db, cache, lang_type, vocab_cf, client, search_clear):
    data = client.get(
        "/api/vocabularies/",
        headers=[
            ("Accept", "application/vnd.inveniordm.v1+json"),
        ],
    ).json

    assert data["hits"]["hits"][0]["title_l10n"] == "languages"
    assert data["hits"]["hits"][0]["description_l10n"] == "czech language vocabulary type."

    data = client.get(
        "/api/vocabularies/",
        headers=[
            ("Accept-Language", "cs"),
            ("Accept", "application/vnd.inveniordm.v1+json"),
        ],
    ).json

    assert data["hits"]["hits"][0]["title_l10n"] == "jazyky"
    assert data["hits"]["hits"][0]["description_l10n"] == "slovnikovy typ ceskeho jazyka."

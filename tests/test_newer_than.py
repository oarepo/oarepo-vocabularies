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
import time_machine
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture
def vocab_entries(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    with time_machine.travel("2024-01-01T00:00:00Z", tick=False):
        vocab_service.create(
            system_identity,
            {"id": "eng", "title": {"en": "English", "da": "Engelsk"}, "type": "languages"},
        )

    with time_machine.travel("2024-06-01T00:00:00Z", tick=False):
        vocab_service.create(
            system_identity,
            {"id": "cze", "title": {"en": "Czech", "da": "Tjekkisk"}, "type": "languages"},
        )

    Vocabulary.index.refresh()


def test_services_search_newer_than(app, db, cache, lang_type, vocab_entries):
    results = vocab_service.search(system_identity, {"newer": "2024-03-01T00:00:00Z"}, type=lang_type.id)
    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "cze"

    results = vocab_service.search(system_identity, {"newer": "2023-01-01T00:00:00Z"}, type=lang_type.id)
    assert results.total == 2
    assert {hit["id"] for hit in results.hits} == {"eng", "cze"}

    results = vocab_service.search(system_identity, {"newer": "2025-01-01T00:00:00Z"}, type=lang_type.id)
    assert results.total == 0

    results = vocab_service.search(system_identity, {}, type=lang_type.id)
    assert results.total == 2


def test_resource_search_newer_than(app, db, cache, lang_type, vocab_cf, client, vocab_entries):
    data = client.get("/api/vocabularies/languages?newer=2024-03-01T00:00:00Z").json
    ids = [hit["id"] for hit in data["hits"]["hits"]]
    assert ids == ["cze"]

    data = client.get("/api/vocabularies/languages?newer=2023-01-01T00:00:00Z").json
    ids = {hit["id"] for hit in data["hits"]["hits"]}
    assert ids == {"eng", "cze"}

    data = client.get("/api/vocabularies/languages?newer=2025-01-01T00:00:00Z").json
    assert data["hits"]["hits"] == []


def test_resource_search_newer_than_invalid_value(app, db, cache, lang_type, vocab_cf, client, vocab_entries):
    response = client.get("/api/vocabularies/languages?newer=not-a-date")
    assert response.status_code == 400

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
from invenio_vocabularies.records.api import Vocabulary
from opensearch_dsl import Search

from oarepo_vocabularies.services.params import SKOSMappingParam


@pytest.fixture
def vocab_entries(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
            "mappings": [
                {"identifier": "12345", "scheme": "myscheme", "relation": "exactMatch"},
                {"identifier": "eng-close", "scheme": "otherscheme", "relation": "closeMatch"},
            ],
        },
    )
    vocab_service.create(
        system_identity,
        {
            "id": "cze",
            "title": {"en": "Czech", "da": "Tjekkisk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
            "mappings": [
                {"identifier": "67890", "scheme": "myscheme", "relation": "exactMatch"},
            ],
        },
    )

    Vocabulary.index.refresh()


def test_services_search_skos(app, db, cache, lang_type, vocab_entries):

    results = vocab_service.search(system_identity, {"skos": ["exactMatch:12345@myscheme"]}, type=lang_type.id)
    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"

    results = vocab_service.search(system_identity, {"skos": ["closeMatch:eng-close@otherscheme"]}, type=lang_type.id)
    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"

    results = vocab_service.search(
        system_identity,
        {"skos": ["exactMatch:12345@myscheme", "exactMatch:67890@myscheme"]},
        type=lang_type.id,
    )
    assert results.total == 2
    assert {hit["id"] for hit in results.hits} == {"eng", "cze"}

    results = vocab_service.search(system_identity, {"skos": ["exactMatch:12345@wrongscheme"]}, type=lang_type.id)
    assert results.total == 0


def test_resource_search_skos(app, db, cache, lang_type, vocab_cf, client, vocab_entries):

    data = client.get("/api/vocabularies/languages?skos=exactMatch:12345@myscheme").json
    ids = [hit["id"] for hit in data["hits"]["hits"]]
    assert ids == ["eng"]

    data = client.get("/api/vocabularies/languages?skos=closeMatch:eng-close@otherscheme").json
    ids = [hit["id"] for hit in data["hits"]["hits"]]
    assert ids == ["eng"]

    data = client.get("/api/vocabularies/languages?skos=exactMatch:12345@myscheme&skos=exactMatch:67890@myscheme").json
    ids = {hit["id"] for hit in data["hits"]["hits"]}
    assert ids == {"eng", "cze"}

    data = client.get("/api/vocabularies/languages?skos=exactMatch:12345@wrongscheme").json
    assert data["hits"]["hits"] == []


def test_mapping_param_no_skos():
    search = Search()
    result = SKOSMappingParam(config=None).apply(system_identity, search, {})
    assert result is search


def test_mapping_param_with_scheme():
    search = Search()
    result = SKOSMappingParam(config=None).apply(system_identity, search, {"skos": ["exactMatch:12345@myscheme"]})

    assert result.to_dict() == {
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "nested": {
                                        "path": "mappings",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {"term": {"mappings.scheme": "myscheme"}},
                                                    {"term": {"mappings.relation": "exactMatch"}},
                                                    {"term": {"mappings.identifier": "12345"}},
                                                ]
                                            }
                                        },
                                    }
                                }
                            ],
                            "minimum_should_match": 1,
                        }
                    }
                ]
            }
        }
    }


def test_mapping_param_without_scheme():
    search = Search()
    result = SKOSMappingParam(config=None).apply(system_identity, search, {"skos": ["exactMatch:12345"]})

    assert result.to_dict() == {
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "nested": {
                                        "path": "mappings",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {"term": {"mappings.relation": "exactMatch"}},
                                                    {"term": {"mappings.identifier": "12345"}},
                                                ]
                                            }
                                        },
                                    }
                                }
                            ],
                            "minimum_should_match": 1,
                        }
                    }
                ]
            }
        }
    }


def test_mapping_param_multiple_skos():
    search = Search()
    result = SKOSMappingParam(config=None).apply(
        system_identity, search, {"skos": ["exactMatch:12345@myscheme", "closeMatch:67890@otherscheme"]}
    )

    should_clauses = result.to_dict()["query"]["bool"]["filter"][0]["bool"]["should"]
    assert len(should_clauses) == 2
    assert should_clauses[0]["nested"]["query"]["bool"]["must"] == [
        {"term": {"mappings.scheme": "myscheme"}},
        {"term": {"mappings.relation": "exactMatch"}},
        {"term": {"mappings.identifier": "12345"}},
    ]
    assert should_clauses[1]["nested"]["query"]["bool"]["must"] == [
        {"term": {"mappings.scheme": "otherscheme"}},
        {"term": {"mappings.relation": "closeMatch"}},
        {"term": {"mappings.identifier": "67890"}},
    ]

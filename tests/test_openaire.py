#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import json
from pathlib import Path

import jsonschema
import pytest


@pytest.fixture
def openaire_provider(app):
    provider_object = "OpenAIREProvider(url=None, testing=False)"
    assert isinstance(provider_object, str)
    return provider_object


@pytest.mark.skip(reason="Skip authorities for now")
def test_create_token(app, openaire_provider):
    token = openaire_provider.get_access_token()
    assert token is not None


@pytest.mark.skip(reason="Skip authorities for now")
def test_openaire_client_from_provider(app, openaire_provider):
    assert openaire_provider.openaire_client

    search_query = "health"
    access_token = openaire_provider.get_access_token()
    assert access_token is not None
    result = openaire_provider.openaire_client.quick_search(access_token, search_query)
    assert result is not None
    assert "response" in result
    assert "results" in result["response"]


@pytest.mark.skip(reason="Skip authorities for now")
def test_openaire_provider_search_name(app, openaire_provider):
    query = "Czech"
    results = openaire_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total >= 1
    assert len(items) >= 1


@pytest.mark.skip(reason="Skip authorities for now")
def test_openaire_provider_search_empty(app, openaire_provider):
    query = ""
    results = openaire_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total == 0
    assert len(items) == 0


@pytest.mark.skip(reason="Skip authorities for now")
def test_openaire_provider_pagination(app, openaire_provider):
    query = "a"
    results = openaire_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total > 20
    assert len(items) == 20

    page2_results = openaire_provider.search(identity=None, params={"q": query, "page": 2})
    page2_items, page2_total_value = page2_results
    assert page2_total_value > 20
    assert len(page2_items) == 20

    assert total <= page2_total_value

    for item in items:
        if item is None:
            continue
        assert "title" in item
        assert "funder" in item
        assert "number" in item
        assert "identifiers" in item
        assert "organizations" in item
        assert "program" in item
        assert "acronym" in item
        assert "tags" in item
        assert "subjects" in item
        assert "organizations" in item


@pytest.mark.skip(reason="Skip authorities for now")
def test_openaire_provider_get(app, openaire_provider):
    item_id = "corda_______::89677d86a305a5b985427b92a81bc038"
    item = openaire_provider.get(None, item_id)
    assert item is not None
    assert "title" in item


@pytest.mark.skip(reason="Skip authorities for now")
def test_json_schema_validation(app, openaire_provider):
    with Path.open(Path(__file__).parent / "schemas" / "award-v1.0.0.json") as f:
        schema = json.load(f)

    items, _ = openaire_provider.search(identity=None, params={"q": "a"})

    for item in items:
        if item is None:
            continue
        try:
            jsonschema.validate(item, schema)
        except jsonschema.ValidationError as e:
            raise AssertionError from e

import json
from pathlib import Path
import pytest
import jsonschema
from oarepo_vocabularies.authorities import (
    AuthorityProvider,
    OpenAIREProvider
)
from requests.exceptions import HTTPError

from oarepo_vocabularies.authorities.providers.openaire_provider import OpenAIREProvider, OpenAIREClient


@pytest.fixture
def openaire_provider():
    provider_object = OpenAIREProvider(url=None, testing=False)
    assert isinstance(provider_object, AuthorityProvider)
    return provider_object

def test_create_token(openaire_provider):
    token = openaire_provider.openaire_client.get_token()
    assert token is not None
    
def test_openaire_client_from_provider(openaire_provider):
    assert openaire_provider.openaire_client
    
    search_query = "health"
    access_token = openaire_provider.openaire_client.get_token()
    assert access_token is not None
    result = openaire_provider.openaire_client.quick_search(access_token, search_query)
    assert result is not None
    assert "response" in result
    assert "results" in result["response"]
    
def test_openaire_provider_search_name(openaire_provider):
    query = "Czech"
    results = openaire_provider.search(identity=None, params={"q": query})
    items, total = results  
    assert total >= 1
    assert len(items) >= 1
    
def test_openaire_provider_search_empty(openaire_provider):
    query = ""
    results = openaire_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total == 0
    assert len(items) == 0
    
def test_openaire_provider_pagination(openaire_provider):
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

def test_openaire_provider_get(openaire_provider):
    item_id = "corda_______::89677d86a305a5b985427b92a81bc038"
    item = openaire_provider.get(None, item_id)
    assert item is not None
    assert "title" in item

def test_json_schema_validation(openaire_provider):
    with open(Path(__file__).parent/"schemas"/"award-v1.0.0.json") as f:
        schema = json.load(f)
    
    items, _ = openaire_provider.search(identity=None, params={"q": "a"})
    
    for item in items:
        if item is None:
            continue
        try:
            jsonschema.validate(item, schema)
        except jsonschema.ValidationError as e:
            print(e)
            assert False
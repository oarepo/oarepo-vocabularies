
import json
import pytest
import os
import jsonschema
from oarepo_vocabularies.authorities import (
    AuthorityProvider,
    ORCIDProvider
)
from requests.exceptions import HTTPError

from oarepo_vocabularies.authorities.providers.orcid_provider import ORCIDProvider, ORCIDClient



@pytest.fixture
def orcid_provider():
    provider_object = ORCIDProvider(url=None, testing=False)
    assert isinstance(provider_object, AuthorityProvider)
    return provider_object

def test_orcid_client_from_provider(orcid_provider):
    
    assert orcid_provider.orcid_client
    
    orcid_id = "0000-0002-8584-7715"
    access_token = orcid_provider.orcid_client.get_search_token_from_orcid()
    result = orcid_provider.orcid_client.get_record(access_token=access_token, orcid_id=orcid_id)
    assert result["orcid-identifier"]["path"] == orcid_id

    bad_orcid_id = "0000-0000-0000-0000"
    with pytest.raises(HTTPError):
        orcid_provider.orcid_client.get_record(None, bad_orcid_id)

def test_orcid_provider_search_name(orcid_provider):
    query = "Radek Cibulka"
    results = orcid_provider.search(identity=None, params={"q": query})
    items, total = results  
    assert total >= 1
    assert len(items) >= 1
    
def test_orcid_provider_search_empty(orcid_provider):
    query = ""
    results = orcid_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total == 0
    assert len(items) == 0

def test_orcid_provider_pagination(orcid_provider):
    query = "a"
    results = orcid_provider.search(identity=None, params={"q": query})
    items, total = results
    assert total > 20
    assert len(items) == 20

    page2_results = orcid_provider.search(identity=None, params={"q": query, "page": 2})
    page2_items, page2_total_value = page2_results
    assert page2_total_value > 20
    assert len(page2_items) == 20

    assert total == page2_total_value

    for item in items:
        if item is None:
            continue
        assert item["name"] != ""
        assert item["identifiers"][0]["identifier"] not in [it["identifiers"][0]["identifier"] for it in page2_items]
        
def test_json_schema_validation(orcid_provider):
    with open("schemas/name-v1.0.0.json") as f:
        schema = json.load(f)
    
    items, _ = orcid_provider.search(identity=None, params={"q": "a"})
    
    for item in items:
        if item is None:
            continue
        try:
            jsonschema.validate(item, schema)
        except jsonschema.ValidationError as e:
            print(e)
            assert False

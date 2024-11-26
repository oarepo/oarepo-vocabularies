import json
from pathlib import Path
import pytest
import os
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
import math
from urllib.parse import urlparse

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_vocabularies.proxies import current_service as vocabulary_service

from oarepo_vocabularies.authorities.providers import RORProviderV2
from oarepo_vocabularies.records.api import Vocabulary


def test_authority_resource(
    client, authority_rec, authority_type, ror_authority_type, search_clear
):
    # Arrange.

    # Act.
    params = "q=affiliation&page=1&size=2"
    resp = client.get(f"/api/vocabularies/authority/authoritative?{params}").json

    # Assert.
    results = resp["hits"]["hits"]

    external_result = [res for res in results if res["props"]["external"]]
    assert len(external_result) == 1
    assert external_result[0]["id"] == "03zsq2967"

    internal_result = [res for res in results if not res["props"]["external"]]
    assert len(internal_result) == 1
    assert internal_result[0]["id"] == "020bcb226"

    # Test ROR authority resource
    params = "q=cesnet&page=1"
    resp = client.get(f"/api/vocabularies/ror-authority/authoritative?{params}").json
    # Assert.
    results = resp["hits"]["hits"]

    external_result = [res for res in results if res["props"]["external"]]
    assert len(external_result) == 1
    assert external_result[0]["id"] == "ror:050dkka69"

    # Test for pagination
    assert "links" in resp.keys()
    assert "next" not in resp["links"]
    assert "prev" not in resp["links"]

    params = "q=c&page=1"
    resp = client.get(f"/api/vocabularies/ror-authority/authoritative?{params}").json
    page1_results = resp["hits"]["hits"]
    assert "links" in resp.keys()
    assert "next" in resp["links"].keys()
    assert "prev" not in resp["links"].keys()
    next_link = urlparse(resp["links"]["next"])
    assert next_link.path == "/api/vocabularies/ror-authority/authoritative"
    assert "page=2" in next_link.query

    resp = client.get(next_link.geturl()).json
    page2_results = resp["hits"]["hits"]
    assert page2_results[0]["id"] != page1_results[0]["id"]
    assert "next" in resp["links"].keys()
    assert "prev" in resp["links"].keys()
    prev_link = urlparse(resp["links"]["prev"])
    assert "page=1" in prev_link.query

    # Test last page
    page_size = 20
    total = resp["hits"]["total"]
    last_page = math.floor(total / page_size)

    params = f"q=c&page={last_page + 1}"
    resp = client.get(f"/api/vocabularies/ror-authority/authoritative?{params}").json
    last_page_results = resp["hits"]["hits"]
    assert len(last_page_results) == total - (last_page * page_size)


def test_submit_record_fetch_authority(
    search_clear,
    identity,
    authority_type,
    ror_authority_type,
    simple_record_service,
    vocab_cf,
):
    response = simple_record_service.create(
        identity,
        {
            "title": "a",
            "authority": {"id": "03zsq2967"},
            "ror-authority": {"id": "ror:050dkka69"},
        },
    )
    assert response.data["authority"]["id"] == "03zsq2967"
    assert response.data["authority"]["title"] == {
        "en": "Association of Asian Pacific Community Health Organizations"
    }

    assert response.data["ror-authority"]["id"] == "ror:050dkka69"
    print(response.data["ror-authority"])
    assert response.data["ror-authority"]["title"] == {
        "en": "Czech Education and Scientific Network"
    }

    # check that the vocabulary item has been created
    Vocabulary.index.refresh()
    assert vocabulary_service.read(identity, ("authority", "03zsq2967")).data[
        "title"
    ] == {"en": "Association of Asian Pacific Community Health Organizations"}

    assert vocabulary_service.read(identity, ("ror-authority", "ror:050dkka69")).data[
        "title"
    ] == {"en": "Czech Education and Scientific Network"}
    return response.id


def test_ror_authority_result_to_vocabulary(example_ror_record):
    vocab_item = RORProviderV2.to_vocabulary_item(example_ror_record)

    # Test id is provided
    assert vocab_item["id"] == "ror:050dkka69"

    # Test title is converted
    assert vocab_item["title"] == {"en": "Czech Education and Scientific Network"}

    # Test other supported props is converted
    assert len(vocab_item["props"].keys()) > 0
    assert vocab_item["props"]["acronyms"] == "CESNET"


def test_submit_record_update_authority(
    search_clear,
    identity,
    authority_type,
    ror_authority_type,
    simple_record_service,
    vocab_cf,
):
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(identity, ("authority", "03zsq2967"))
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(identity, ("authority", "ror:050dkka69"))

    record_id = test_submit_record_fetch_authority(
        search_clear,
        identity,
        authority_type,
        ror_authority_type,
        simple_record_service,
        vocab_cf,
    )
    response = simple_record_service.update(
        identity,
        record_id,
        {
            "title": "b",
            "authority": {"id": "020bcb226"},
            "ror-authority": {"id": "ror:050dkka69"},
        },
    )
    assert response.data["authority"]["id"] == "020bcb226"
    assert response.data["authority"]["title"] == {"en": "Oakton Community College"}

    assert response.data["ror-authority"]["id"] == "ror:050dkka69"
    print(response.data["ror-authority"])
    assert response.data["ror-authority"]["title"] == {
        "en": "Czech Education and Scientific Network"
    }

    # check that the vocabulary item has been created
    Vocabulary.index.refresh()
    assert vocabulary_service.read(identity, ("authority", "020bcb226")).data[
        "title"
    ] == {"en": "Oakton Community College"}

    assert vocabulary_service.read(identity, ("ror-authority", "ror:050dkka69")).data[
        "title"
    ] == {"en": "Czech Education and Scientific Network"}

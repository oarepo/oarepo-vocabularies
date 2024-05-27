from invenio_vocabularies.proxies import current_service as vocabulary_service

from oarepo_vocabularies.authorities.results import to_vocabulary_item
from oarepo_vocabularies.records.api import Vocabulary


def test_authority_resource(client, authority_rec, authority_type, search_clear):
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


def test_ror_authority_result_to_vocabulary(example_ror_record):
    vocab_item = to_vocabulary_item(example_ror_record)

    # Test id is provided
    assert vocab_item['id'] == example_ror_record['id']

    # Test title is converted
    assert vocab_item['title'] == {
        'en': 'Czech Education and Scientific Network'
    }

    # Test other supported props is converted
    assert vocab_item['props'] != {}


def test_submit_record_fetch_authority(
    search_clear, identity, authority_type, simple_record_service, vocab_cf
):
    response = simple_record_service.create(
        identity, {"title": "a", "authority": {"id": "03zsq2967"}}
    )
    assert response.data["authority"]["id"] == "03zsq2967"
    assert response.data["authority"]["title"] == {
        "en": "Association of Asian Pacific Community Health Organizations"
    }
    # check that the vocabulary item has been created
    Vocabulary.index.refresh()
    assert vocabulary_service.read(identity, ("authority", "03zsq2967")).data[
        "title"
    ] == {"en": "Association of Asian Pacific Community Health Organizations"}

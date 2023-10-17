from invenio_vocabularies.proxies import current_service as vocab_service

from oarepo_vocabularies.records.api import Vocabulary


def test_save_with_props(
    search_clear,
    identity,
    authority_type,
    simple_record_service,
    vocab_cf,
    lang_data,
    lang_type,
):
    vocab_service.create(identity, lang_data)
    Vocabulary.index.refresh()

    response = simple_record_service.create(
        identity, {"title": "a", "lng": {"id": "eng", "props": {"a": "b"}}}
    )
    print(response.data)
    assert response.data["lng"]["id"] == "eng"
    assert response.data["lng"]["title"] == {"en": "English"}

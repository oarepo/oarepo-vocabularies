import pytest
from invenio_pidstore.errors import PIDDeletedError

from oarepo_vocabularies_basic.records.api import OARepoVocabularyBasic


def test_create(lang_type, lang_data, basic_service, identity):
    item = basic_service.create(identity, lang_data)

    assert item.id == lang_data["id"]
    for k, v in lang_data.items():
        assert item.data[k] == v

    # Read it
    read_item = basic_service.read(identity, ("languages", "eng"))

    assert item.id == read_item.id
    assert item.data == read_item.data
    assert read_item.data["type"] == "languages"


def test_update(lang_type, lang_record, basic_service, identity):
    _id = lang_record['id']

    data = {**lang_record.data, 'title': {'en': 'test'}}

    basic_service.update(identity, ("languages", "eng"), data)

    # Read it
    read_item = basic_service.read(identity, ("languages", "eng"))
    assert _id == read_item.id
    read_data = {**read_item.data}
    read_data.pop('created')
    read_data.pop('updated')
    read_data.pop('links')
    assert read_data.pop('revision_id') == 2
    assert data == read_data


def test_delete(lang_type, lang_record, basic_service, identity):
    basic_service.delete(identity, ("languages", "eng"))

    with pytest.raises(PIDDeletedError):
        basic_service.read(identity, ("languages", "eng"))


def test_search(lang_type, lang_record, basic_service, identity):
    OARepoVocabularyBasic.index.refresh()

    hits = basic_service.search(identity, params={'q': 'title.en:English'}, type='languages')
    data = list(hits.hits)
    assert len(data) == 1

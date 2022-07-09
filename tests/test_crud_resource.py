#
# Tests
#

from oarepo_vocabularies.basic.records.api import OARepoVocabularyBasic
from tests.utils import replace_timestamps


def test_create(app, client_with_credentials, lang_type, lang_data, h):
    """Test the endpoint to retrieve a single item."""
    res = client_with_credentials.post(f'/v/{lang_type.id}', json=lang_data)

    assert res.status_code == 201
    assert res.json["id"] == lang_data['id']
    # Test links
    assert res.json["links"] == {
        'children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=children',
        'descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=descendants',
        'self': 'https://127.0.0.1:5000/api/v/languages/eng',
        'self+children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+children',
        'self+descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+descendants'
    }


def test_create_in_vocabs(app, client_with_credentials, lang_type, lang_data, h):
    # for url in app.url_map._rules:
    #     print(url, url.methods, url.endpoint)
    """Test the endpoint to retrieve a single item."""
    res = client_with_credentials.post(f'/v/', json=lang_data)

    assert res.status_code == 201
    assert res.json["id"] == lang_data['id']
    # Test links
    assert res.json["links"] == {
        'children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=children',
        'descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=descendants',
        'self': 'https://127.0.0.1:5000/api/v/languages/eng',
        'self+children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+children',
        'self+descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+descendants'
    }


def test_get(app, client_with_credentials, lang_type, lang_record):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/{lang_type.id}/{lang_record["id"]}')
    assert res.status_code == 200
    d = res.json
    assert replace_timestamps(d) == {
        'created': "TS", "updated": "TS",
        'description': {'cs': 'Anglický popis', 'en': 'English description'},
        'icon': 'file-o',
        'id': 'eng',
        'links': {'children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=children',
                  'descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=descendants',
                  'self': 'https://127.0.0.1:5000/api/v/languages/eng',
                  'self+children': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+children',
                  'self+descendants': 'https://127.0.0.1:5000/api/v/languages/eng?hierarchy=self+descendants'},
        'revision_id': 1,
        'title': {'cs': 'Angličtina', 'en': 'English'},
        'type': 'languages'}


def test_delete(app, client_with_credentials, lang_type, lang_record):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.delete(f'/v/{lang_type.id}/{lang_record["id"]}')
    assert res.status_code == 204

    res = client_with_credentials.delete(f'/v/{lang_type.id}/{lang_record["id"]}')
    assert res.status_code == 410  # gone, not not found
    assert res.json == {'message': 'The record has been deleted.', 'status': 410}


def test_search(app, client_with_credentials, lang_type, lang_record):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/{lang_type.id}?q=title.en:English')
    assert res.status_code == 200
    d = res.json
    assert d['aggregations']['_schema'] == {'buckets': [{'doc_count': 1,
                                                         'is_selected': False,
                                                         'key': 'local://oarepo-vocabularies.basic-1.0.0.json',
                                                         'label': 'local://oarepo-vocabularies.basic-1.0.0.json'}],
                                            'label': ''}
    assert d['hits']['total'] == 1
    assert d['hits']['hits'][0]['title']['en'] == 'English'
    assert d['links']['self'] == 'https://127.0.0.1:5000/api/v/languages?' \
                                 'page=1&q=title.en%3AEnglish&size=25&sort=bestmatch'

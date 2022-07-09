from oarepo_vocabularies.basic.records.api import OARepoVocabularyBasic
from tests.utils import api_path, replace_timestamps


def test_get_path(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a/b/c')
    assert res.status_code == 200

    d = res.json
    assert replace_timestamps(d) == {
        'id': 'a/b/c',
        'links': {
            'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=ancestors',
            'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=children',
            'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=descendants',
            'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
            'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c',
            'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+ancestors',
            'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+children',
            'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+descendants'
        },
        'revision_id': 1,
        'title': {'en': 'a-b-c'},
        'type': 'hierarchy',
        'created': 'TS',
        'updated': 'TS'
    }


def test_create_on_path(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.post(f'/v/hierarchy/a/b/', json={
        'title': {'en': 'a-b-d'},
        'id': 'd'
    })
    assert res.status_code == 201
    assert res.json['links']['self'] == 'https://127.0.0.1:5000/api/v/hierarchy/a/b/d'


def test_self(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a/b/c')
    assert res.status_code == 200
    res1 = client_with_credentials.get(api_path(res.json['links']['self']))

    assert res.json == res1.json


def test_ancestors(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a/b/c')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['ancestors']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a',
                    'links': {
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=descendants',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                }
            ],
            'total': 2
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=ancestors'},
        'sortBy': 'hierarchy_deepest'
    }


def test_ancestors_self(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a/b/c')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['self+ancestors']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a/b/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a',
                    'links': {
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=descendants',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                }
            ],
            'total': 3
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self%2Bancestors'},
        'sortBy': 'hierarchy_deepest'
    }


def test_children(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['children']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'}],
            'total': 3
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=children'},
        'sortBy': 'id'
    }


def test_children_self(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['self+children']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a',
                    'links': {
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=descendants',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                }
            ],
            'total': 4
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self%2Bchildren'},
        'sortBy': 'id'
    }


def test_descendants(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['descendants']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                }
            ],
            'total': 12
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=descendants'},
        'sortBy': 'id'
    }


def test_descendants_self(app, client_with_credentials, basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/hierarchy/a')
    assert res.status_code == 200
    res = client_with_credentials.get(api_path(res.json['links']['self+descendants']))

    data = res.json
    assert replace_timestamps(data) == {
        'hits': {
            'hits': [
                {
                    'created': 'TS',
                    'id': 'a',
                    'links': {
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=descendants',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/b/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/b',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/b/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-b-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/a',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/a?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-a'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/b',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/b?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-b'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                },
                {
                    'created': 'TS',
                    'id': 'a/c/c',
                    'links': {
                        'ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=ancestors',
                        'children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=children',
                        'descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=descendants',
                        'parent': 'https://127.0.0.1:5000/api/v/hierarchy/a/c',
                        'self': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c',
                        'self+ancestors': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+ancestors',
                        'self+children': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+children',
                        'self+descendants': 'https://127.0.0.1:5000/api/v/hierarchy/a/c/c?hierarchy=self+descendants'},
                    'revision_id': 1,
                    'title': {'en': 'a-c-c'},
                    'type': 'hierarchy',
                    'updated': 'TS'
                }
            ],
            'total': 13
        },
        'links': {'self': 'https://127.0.0.1:5000/api/v/hierarchy/a?hierarchy=self%2Bdescendants'},
        'sortBy': 'id'
    }

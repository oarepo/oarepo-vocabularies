import pytest
from invenio_records_resources.services.records.results import RecordList

from oarepo_vocabularies.services.service import NoParentError
from oarepo_vocabularies.basic.records.api import OARepoVocabularyBasic


def test_parent(basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    parent_rec = basic_service.parent(identity, id_=('hierarchy', 'a/b/c'))
    assert parent_rec['id'] == 'a/b'

    with pytest.raises(NoParentError):
        basic_service.parent(identity, id_=('hierarchy', 'a'))


def test_ancestors(basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    ancestors: RecordList = basic_service.ancestors(identity, id_=('hierarchy', 'a/b/c'))
    hits = list(ancestors.hits)
    assert len(ancestors) == 2
    assert hits[0]['id'] == 'a/b'
    assert hits[1]['id'] == 'a'

    ancestors: RecordList = basic_service.ancestors(identity, id_=('hierarchy', 'a/b/c'), with_self=True)
    hits = list(ancestors.hits)
    assert len(ancestors) == 3
    assert hits[0]['id'] == 'a/b/c'
    assert hits[1]['id'] == 'a/b'
    assert hits[2]['id'] == 'a'

    ancestors: RecordList = basic_service.ancestors(identity, id_=('hierarchy', 'a'))
    assert len(ancestors) == 0

    ancestors: RecordList = basic_service.ancestors(identity, id_=('hierarchy', 'a'), with_self=True)
    hits = list(ancestors.hits)
    assert len(ancestors) == 1
    assert hits[0]['id'] == 'a'


def test_descendants(basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    descendants: RecordList = basic_service.descendants(identity, id_=('hierarchy', 'a/b/c'), with_self=True)
    assert len(descendants) == 1
    hits = list(descendants.hits)
    assert hits[0]['id'] == 'a/b/c'

    descendants: RecordList = basic_service.descendants(identity, id_=('hierarchy', 'a/b/c'), with_self=False)
    assert len(descendants) == 0

    descendants: RecordList = basic_service.descendants(identity, id_=('hierarchy', 'a/b'), with_self=False)
    assert len(descendants) == 3
    hits = list(descendants.hits)
    assert hits[0]['id'] == 'a/b/a'
    assert hits[1]['id'] == 'a/b/b'
    assert hits[2]['id'] == 'a/b/c'

    descendants: RecordList = basic_service.descendants(identity, id_=('hierarchy', 'a/b'), with_self=True)
    assert len(descendants) == 4
    hits = list(descendants.hits)
    assert hits[0]['id'] == 'a/b'
    assert hits[1]['id'] == 'a/b/a'
    assert hits[2]['id'] == 'a/b/b'
    assert hits[3]['id'] == 'a/b/c'

    descendants: RecordList = basic_service.descendants(identity, id_=('hierarchy', 'a'), with_self=False)
    assert len(descendants) == 12
    hits = list(descendants.hits)
    assert hits[0]['id'] == 'a/a'
    assert hits[1]['id'] == 'a/a/a'
    assert hits[2]['id'] == 'a/a/b'
    assert hits[3]['id'] == 'a/a/c'
    assert hits[4]['id'] == 'a/b'
    assert hits[5]['id'] == 'a/b/a'
    assert hits[6]['id'] == 'a/b/b'
    assert hits[7]['id'] == 'a/b/c'
    assert hits[8]['id'] == 'a/c'
    assert hits[9]['id'] == 'a/c/a'
    assert hits[10]['id'] == 'a/c/b'
    assert hits[11]['id'] == 'a/c/c'


def test_children(basic_service, identity, hierarchy_records):
    OARepoVocabularyBasic.index.refresh()

    children: RecordList = basic_service.children(identity, id_=('hierarchy', 'a/b/c'))
    assert len(children) == 0

    children: RecordList = basic_service.children(identity, id_=('hierarchy', 'a/b'))
    assert len(children) == 3
    hits = list(children.hits)
    assert hits[0]['id'] == 'a/b/a'
    assert hits[1]['id'] == 'a/b/b'
    assert hits[2]['id'] == 'a/b/c'

    children: RecordList = basic_service.children(identity, id_=('hierarchy', 'a'))
    assert len(children) == 3
    hits = list(children.hits)
    assert hits[0]['id'] == 'a/a'
    assert hits[1]['id'] == 'a/b'
    assert hits[2]['id'] == 'a/c'

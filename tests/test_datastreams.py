import json
import os

from invenio_access.permissions import system_identity
from invenio_vocabularies.datastreams import StreamEntry

from oarepo_vocabularies.basic.records.api import OARepoVocabularyBasic
from oarepo_vocabularies.datastreams.catalogue import YAMLVocabularyCatalogue
from oarepo_vocabularies.datastreams.excel import ExcelReader
from oarepo_vocabularies.datastreams.hierarchy import HierarchyTransformer
from tests.utils import replace_timestamps

FUNDERS_FILE = os.path.join(os.path.dirname(__file__), 'data/funders.xlsx')
INSTITUTIONS_FILE = os.path.join(os.path.dirname(__file__), 'data/institutions.xlsx')
FUNDERS_LOADED_FILE = os.path.join(os.path.dirname(__file__), 'data/funders-loaded.json')
INSTITUTIONS_TRANSFORMED_FILE = os.path.join(os.path.dirname(__file__), 'data/institutions-transformed.json')
CATALOGUE_FILE = os.path.join(os.path.dirname(__file__), 'data/catalogue.yaml')


def test_excel_reader():
    rdr = ExcelReader(
        vocabulary_type='funders', origin=FUNDERS_FILE)
    data = list(rdr.read())
    with open(FUNDERS_LOADED_FILE, 'r') as f:
        expected_data = json.load(f)
    assert data == expected_data


def test_hierarchy_transformer():
    rdr = ExcelReader(
        vocabulary_type='institutions', origin=INSTITUTIONS_FILE)
    tr = HierarchyTransformer()
    data = [StreamEntry(x) for x in rdr.read()]
    for d in data:
        tr.apply(d)
    data = [x.entry for x in data]
    with open(INSTITUTIONS_TRANSFORMED_FILE, 'r') as f:
        expected_data = json.load(f)
    assert data == expected_data


def test_load_vocabulary(app, basic_service, client_with_credentials):
    YAMLVocabularyCatalogue().create_or_update_vocabularies(CATALOGUE_FILE, system_identity)
    OARepoVocabularyBasic.index.refresh()

    res = client_with_credentials.get(f'/v/test/a')
    assert res.status_code == 200
    data = res.json
    assert replace_timestamps(data) == {
        'created': 'TS',
        'id': 'a',
        'links': {
            'children': 'https://127.0.0.1:5000/api/v/test/a?hierarchy=children',
            'descendants': 'https://127.0.0.1:5000/api/v/test/a?hierarchy=descendants',
            'self': 'https://127.0.0.1:5000/api/v/test/a',
            'self+children': 'https://127.0.0.1:5000/api/v/test/a?hierarchy=self+children',
            'self+descendants': 'https://127.0.0.1:5000/api/v/test/a?hierarchy=self+descendants'
        },
        'revision_id': 1,
        'title': {'cs': 'A cs', 'en': 'A en'},
        'type': 'test',
        'updated': 'TS'
    }

    res = client_with_credentials.get(f'/v/test/a/b')
    assert res.status_code == 200
    data = res.json
    assert replace_timestamps(data) == {
        'created': 'TS',
        'id': 'a/b',
        'links': {
            'ancestors': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=ancestors',
            'children': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=children',
            'descendants': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=descendants',
            'parent': 'https://127.0.0.1:5000/api/v/test/a',
            'self': 'https://127.0.0.1:5000/api/v/test/a/b',
            'self+ancestors': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=self+ancestors',
            'self+children': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=self+children',
            'self+descendants': 'https://127.0.0.1:5000/api/v/test/a/b?hierarchy=self+descendants'
        },
        'revision_id': 1,
        'title': {'cs': 'B cs', 'en': 'B en'},
        'type': 'test',
        'updated': 'TS'
    }

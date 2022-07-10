import json
import os

from invenio_vocabularies.datastreams import StreamEntry

from oarepo_vocabularies.datastreams.excel import ExcelReader
from oarepo_vocabularies.datastreams.hierarchy import HierarchyTransformer

FUNDERS_FILE = os.path.join(os.path.dirname(__file__), 'data/funders.xlsx')
INSTITUTIONS_FILE = os.path.join(os.path.dirname(__file__), 'data/institutions.xlsx')


def test_excel_reader():
    rdr = ExcelReader(
        vocabulary_type='funders', origin=FUNDERS_FILE)
    data = list(rdr.read())
    with open('data/funders-loaded.json', 'r') as f:
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
    with open('data/institutions-transformed.json', 'r') as f:
        expected_data = json.load(f)
    assert data == expected_data

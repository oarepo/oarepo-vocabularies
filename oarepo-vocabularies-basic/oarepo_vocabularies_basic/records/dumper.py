from invenio_records.dumpers import SearchDumper as InvenioElasticsearchDumper
from oarepo_vocabularies.records.dumper import OARepoVocabularyDumperBase


class OARepoVocabulariesBasicDumper(
    OARepoVocabularyDumperBase, InvenioElasticsearchDumper
):
    """OARepoVocabularyBasic elasticsearch dumper."""

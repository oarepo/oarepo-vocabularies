from invenio_records.dumpers import ElasticsearchDumper as InvenioElasticsearchDumper
from oarepo_vocabularies.records.dumper import OARepoVocabularyDumperBase


class OARepoVocabulariesBasicDumper(
    OARepoVocabularyDumperBase, InvenioElasticsearchDumper
):
    """OARepoVocabularyBasic elasticsearch dumper."""

from invenio_records_resources.resources import (
    RecordResourceConfig as InvenioRecordResourceConfig,
)
from oarepo_vocabularies.resources.config import OARepoVocabulariesResourceConfigBase


class OARepoVocabulariesBasicResourceConfig(
    OARepoVocabulariesResourceConfigBase, InvenioRecordResourceConfig
):
    """OARepoVocabularyBasic resource config."""

    blueprint_name = "OARepoVocabulariesBasic"
    url_prefix = "/v/"

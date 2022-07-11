from invenio_records_resources.services import RecordService as InvenioRecordService
from oarepo_vocabularies.services.service import OARepoVocabulariesServiceBase


class OARepoVocabulariesBasicService(
    OARepoVocabulariesServiceBase, InvenioRecordService
):
    """OARepoVocabularyBasic service."""

from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from oarepo_vocabularies.services.config import OARepoVocabulariesServiceConfigBase
from oarepo_vocabularies_basic.records.api import OARepoVocabularyBasic
from oarepo_vocabularies_basic.services.permissions import (
    OARepoVocabulariesBasicPermissionPolicy,
)
from oarepo_vocabularies_basic.services.schema import OARepoVocabulariesBasicSchema
from oarepo_vocabularies_basic.services.search import (
    OARepoVocabulariesBasicSearchOptions,
)


class OARepoVocabulariesBasicServiceConfig(
    OARepoVocabulariesServiceConfigBase, InvenioRecordServiceConfig
):
    """OARepoVocabularyBasic service config."""

    permission_policy_cls = OARepoVocabulariesBasicPermissionPolicy
    schema = OARepoVocabulariesBasicSchema
    search = OARepoVocabulariesBasicSearchOptions
    record_cls = OARepoVocabularyBasic

    components = [*OARepoVocabulariesServiceConfigBase.components]

    model = "oarepo_vocabularies_basic"

from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from invenio_records_resources.services.records.components import (
    DataComponent,
    MetadataComponent,
)

from oarepo_vocabularies.basic.records.api import OARepoVocabularyBasic
from oarepo_vocabularies.basic.services.permissions import (
    OARepoVocabulariesBasicPermissionPolicy,
)
from oarepo_vocabularies.basic.services.schema import OARepoVocabulariesBasicSchema
from oarepo_vocabularies.basic.services.search import (
    OARepoVocabulariesBasicSearchOptions,
)
from oarepo_vocabularies.services.config import OARepoVocabulariesServiceConfigBase


class OARepoVocabulariesBasicServiceConfig(
    OARepoVocabulariesServiceConfigBase, InvenioRecordServiceConfig
):
    """OARepoVocabularyBasic service config."""

    permission_policy_cls = OARepoVocabulariesBasicPermissionPolicy
    schema = OARepoVocabulariesBasicSchema
    search = OARepoVocabulariesBasicSearchOptions
    record_cls = OARepoVocabularyBasic

    components = OARepoVocabulariesServiceConfigBase.components

    model = "basic"

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as InvenioBaseRecord
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext
from oarepo_vocabularies.records.api import OARepoVocabularyBase
from oarepo_vocabularies_basic.records.dumper import OARepoVocabulariesBasicDumper
from oarepo_vocabularies_basic.records.models import OARepoVocabulariesBasicMetadata


class OARepoVocabularyBasic(OARepoVocabularyBase, InvenioBaseRecord):
    model_cls = OARepoVocabulariesBasicMetadata
    schema = ConstantField("$schema", "local://oarepo-vocabularies-basic-1.0.0.json")
    index = IndexField("oarepo_vocabularies_basic-oarepo-vocabularies-basic-1.0.0")

    dumper_extensions = [*OARepoVocabularyBase.dumper_extensions]
    dumper = OARepoVocabulariesBasicDumper(extensions=dumper_extensions)

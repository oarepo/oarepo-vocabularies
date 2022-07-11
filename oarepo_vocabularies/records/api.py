from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.records.api import Record as InvenioBaseRecord
from invenio_records_resources.records.systemfields import PIDField
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider

from oarepo_vocabularies.records.dumper import HierarchyPathExt

from oarepo_vocabularies.records.system_fields.hierarchy import LevelSystemField, HierarchyPathSystemField
from oarepo_vocabularies.records.system_fields.pid_hierarchy import VocabularyHierarchyPIDFieldContext


class OARepoVocabularyBase(Vocabulary, InvenioBaseRecord):
    level = LevelSystemField()
    hierarchy_path = HierarchyPathSystemField()
    dumper_extensions = [IndexedAtDumperExt(), HierarchyPathExt()]
    pid = PIDField(
        "id",
        provider=VocabularyIdProvider,
        context_cls=VocabularyHierarchyPIDFieldContext,
        create=False,
    )

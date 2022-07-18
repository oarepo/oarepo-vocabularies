import oarepo_vocabularies.records.system_fields.pid_hierarchy_relation
import oarepo_vocabularies_basic.records.api
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as InvenioBaseRecord
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext
from mock_module_gen.records.dumper import MockModuleGenDumper
from mock_module_gen.records.models import MockModuleGenMetadata


class MockModuleGenRecord(InvenioBaseRecord):
    model_cls = MockModuleGenMetadata
    schema = ConstantField("$schema", "local://mock-module-gen-1.0.0.json")
    index = IndexField("mock_module_gen-mock-module-gen-1.0.0")

    pid = PIDField(
        create=True, provider=RecordIdProviderV2, context_cls=PIDFieldContext
    )

    dumper_extensions = []
    dumper = MockModuleGenDumper(extensions=dumper_extensions)

    relations = RelationsField(
        hierarchy=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "hierarchy",
            keys=["id", "title"],
            pid_field=oarepo_vocabularies_basic.records.api.OARepoVocabularyBasic.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="hierarchy-relation",
        ),
        hlist=oarepo_vocabularies.records.system_fields.pid_hierarchy_relation.PIDHierarchyRelation(
            "hlist",
            keys=["id", "title"],
            pid_field=oarepo_vocabularies_basic.records.api.OARepoVocabularyBasic.pid.with_type_ctx(
                "hierarchy"
            ),
            cache_key="hlist-relation",
        ),
    )

import inspect
from collections import namedtuple

# from oarepo_runtime.records.relations.base import (
#    RelationsField,  # invenio-records-resources
# )
# from oarepo_runtime.records.systemfields import (
#    ICUSortField,
#    ICUSuggestField,
#    SystemFieldDumperExt,  # neni potreba
# )
# from oarepo_runtime.services.custom_fields import CustomFields, InlinedCustomFields
from flask import current_app
from invenio_records.systemfields import ConstantField, DictField, RelationsField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.systemfields.pid import PIDField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.proxies import current_oarepo_vocabularies
from oarepo_vocabularies.records.systemfields.hierarchy_system_field import (
    HierarchySystemField,
)
from oarepo_vocabularies.records.systemfields.parent_system_field import (
    ParentSystemField,
)
from oarepo_vocabularies.records.systemfields.relations import (
    ParentVocabularyItemRelation,
    ParentVocabularyPIDField,
)


class SpecialVocabulariesAwarePIDFieldContext(VocabularyPIDFieldContext):
    def resolve(self, pid_value):
        if isinstance(pid_value, str):
            pid_type = self._type_id
            item_id = pid_value
        else:
            pid_type, item_id = pid_value

        specialized_service = current_oarepo_vocabularies.get_specialized_service(
            pid_type
        )
        if not specialized_service:
            return super().resolve(pid_value)
        return specialized_service.config.record_cls.pid.resolve(item_id)


class CustomFieldsMixin(MappingSystemFieldMixin):
    def __init__(self, config_key, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config_key = config_key

    @property
    def mapping(self):
        custom_fields = current_app.config[self.config_key]
        return {cf.name: cf.mapping for cf in custom_fields}

    @property
    def mapping_settings(self):
        return {}

    def search_dump(self, data, record):
        custom_fields = current_app.config.get(self.config_key, {})

        for cf in custom_fields:
            cf.dump(data, cf_key=self.key)
        return data

    def search_load(self, data, record_cls):
        custom_fields = current_app.config.get(self.config_key, {})

        for cf in custom_fields:
            cf.load(data, cf_key=self.key)
        return data


class CustomFields(CustomFieldsMixin, DictField):
    def __init__(self, flatten, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flatten = flatten

    @property
    def mapping(self):
        mapping = {self.key: {"type": "object", "properties": super().mapping}}

        if self.flatten:
            return mapping[self.key]["properties"]
        return mapping


class Vocabulary(
    InvenioVocabulary,
):
    pid = PIDField(
        "id",
        provider=VocabularyIdProvider,
        context_cls=SpecialVocabulariesAwarePIDFieldContext,
        create=False,
    )

    # dumper = SearchDumper(
    #    extensions=[
    #        IndexedAtDumperExt(),
    #        SystemFieldDumperExt(),
    ##    ]
    # )
    schema = ConstantField(
        "$schema",
        "local://vocabularies/vocabulary-ext-v1.0.0.json",
    )

    relations = MultiRelationsField(
        parent=ParentVocabularyItemRelation(
            "parent",
            keys=["title"],
            pid_field=ParentVocabularyPIDField(),
            # TODO: pid_field, vlastni class dedi z PIDRelation a nadefinovat vlastni RelationResult
        ),
        custom_fields=CustomFieldsRelation("VOCABULARIES_CF"),
    )

    parent = ParentSystemField()

    hierarchy = HierarchySystemField()
    # sort = ICUSortField(source_field="title")
    # suggest = ICUSuggestField(source_field="title")
    # suggest_hierarchy = ICUSuggestField(source_field="hierarchy.title")

    # pridat to runtime: records/system fields/ custom fields/ updae_all_system_fields_mapings
    # prochazet service a update (jestli jsou relations, vzit a update mapping)

    # custom_fields, hierarchy bude dictfield a pridat element relation
    # https://github.com/inveniosoftware/invenio-rdm-records/blob/bf32413d277fe7642ef98d6eae415f2ef1f02105/invenio_rdm_records/records/api.py#L43
    custom_fields = DictField()


VocabularyRelation = namedtuple(
    "VocabularyRelation", "field_name, field, vocabulary_type"
)


def find_vocabulary_relations(record):
    relations_field_names = [
        x[0]
        for x in inspect.getmembers(
            type(record), lambda x: isinstance(x, RelationsField)
        )
    ]

    for relations_field_name in relations_field_names:
        # iterate all vocabularies there, check that the item exists

        relations = getattr(record, relations_field_name)

        for fld_name in relations:
            fld = getattr(relations, fld_name)
            try:
                pid_context = fld.field.pid_field
            except:
                continue
            if isinstance(pid_context, VocabularyPIDFieldContext):
                yield VocabularyRelation(fld_name, fld, pid_context._type_id)

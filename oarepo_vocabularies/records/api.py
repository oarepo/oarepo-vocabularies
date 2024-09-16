from collections import namedtuple
import inspect
from oarepo_runtime.records.relations.base import RelationsField
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.systemfields import ConstantField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from oarepo_runtime.records.systemfields import (
    ICUSortField,
    ICUSuggestField,
    SystemFieldDumperExt,
)
from oarepo_runtime.services.custom_fields import CustomFields, InlinedCustomFields
from oarepo_runtime.services.relations.mapping import RelationsMapping
from invenio_records_resources.records.systemfields.pid import PIDField
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider

from oarepo_vocabularies.proxies import current_oarepo_vocabularies


class SpecialVocabulariesAwarePIDFieldContext(VocabularyPIDFieldContext):
    def resolve(self, pid_value):
        if isinstance(pid_value, str):
            pid_type = self._type_id
            item_id = pid_value
        else:
            pid_type, item_id = pid_value

        specialized_service = current_oarepo_vocabularies.get_specialized_service(pid_type)
        if not specialized_service:
            return super().resolve(pid_value)
        return specialized_service.config.record_cls.pid.resolve(item_id)


class Vocabulary(InvenioVocabulary):
    pid = PIDField(
        "id",
        provider=VocabularyIdProvider,
        context_cls=SpecialVocabulariesAwarePIDFieldContext,
        create=False,
    )

    dumper = SearchDumper(
        extensions=[
            IndexedAtDumperExt(),
            SystemFieldDumperExt(),
        ]
    )
    schema = ConstantField(
        "$schema",
        "local://vocabularies/vocabulary-ext-v1.0.0.json",
    )

    hierarchy = CustomFields(
        "OAREPO_VOCABULARIES_HIERARCHY_CF",
        "hierarchy",
        clear_none=True,
        create_if_missing=True,
    )
    sort = ICUSortField(source_field="title")
    suggest = ICUSuggestField(source_field="title")
    suggest_hierarchy = ICUSuggestField(source_field="hierarchy.title")

    custom_fields = InlinedCustomFields("VOCABULARIES_CF")


VocabularyRelation = namedtuple(
    "VocabularyRelation", "field_name, field, vocabulary_type"
)


def find_vocabulary_relations(record):
    relations_field_names = [x[0] for x in inspect.getmembers(type(record), lambda x: isinstance(x, RelationsField))]

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

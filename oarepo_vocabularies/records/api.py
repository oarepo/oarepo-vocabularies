from collections import namedtuple

from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.systemfields import ConstantField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from oarepo_runtime.cf import CustomFields, InlinedCustomFields
from oarepo_runtime.records.systemfields import (
    ICUSortField,
    ICUSuggestField,
    SystemFieldDumperExt,
)
from oarepo_runtime.relations.mapping import RelationsMapping


class Vocabulary(InvenioVocabulary):
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

    custom_fields = InlinedCustomFields("OAREPO_VOCABULARIES_CUSTOM_CF")


VocabularyRelation = namedtuple(
    "VocabularyRelation", "field_name, field, vocabulary_type"
)


def find_vocabulary_relations(record):
    # copied from inspect.getmembers, ignoring errors while getting field values
    def getmembers(object, predicate=None):
        results = []
        for key in dir(object):
            try:
                value = getattr(object, key)
            except:
                continue
            if not predicate or predicate(value):
                results.append((key, value))
        results.sort(key=lambda pair: pair[0])
        return results

    relations_fields = getmembers(record, lambda x: isinstance(x, RelationsMapping))

    for relations_field_name, relations in relations_fields:
        # iterate all vocabularies there, check that the item exists
        for fld_name in relations:
            fld = getattr(relations, fld_name)
            try:
                pid_context = fld.field.pid_field
            except:
                continue
            if isinstance(pid_context, VocabularyPIDFieldContext):
                yield VocabularyRelation(fld_name, fld, pid_context._type_id)

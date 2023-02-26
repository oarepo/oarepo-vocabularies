from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.dumpers import CustomFieldsDumperExt
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from oarepo_runtime.cf import CustomFields, InlinedCustomFields


class Vocabulary(InvenioVocabulary):
    dumper = SearchDumper(
        extensions=[
            IndexedAtDumperExt(),
            CustomFieldsDumperExt("OAREPO_VOCABULARIES_HIERARCHY_CF"),
            CustomFieldsDumperExt("OAREPO_VOCABULARIES_CUSTOM_CF"),
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
    custom_fields = InlinedCustomFields("OAREPO_VOCABULARIES_CUSTOM_CF")

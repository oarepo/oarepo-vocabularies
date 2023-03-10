from invenio_records_resources.services.records.params import FilterParam
from invenio_vocabularies.services.service import (
    VocabularySearchOptions as InvenioVocabularySearchOptions,
)


class VocabularySearchOptions(InvenioVocabularySearchOptions):
    params_interpreters_cls = [
        FilterParam.factory(param="h-level", field="hierarchy.level"),
        FilterParam.factory(param="h-parent", field="hierarchy.parent"),
        FilterParam.factory(param="h-ancestor", field="hierarchy.ancestors"),
    ] + InvenioVocabularySearchOptions.params_interpreters_cls
from invenio_records_resources.services.records.params import FilterParam
from invenio_vocabularies.services.service import (
    VocabularySearchOptions as InvenioVocabularySearchOptions,
)
from invenio_records_resources.services import SearchOptions as InvenioSearchOptions


class VocabularySearchOptions(InvenioVocabularySearchOptions):
    params_interpreters_cls = [
        FilterParam.factory(param="h-level", field="hierarchy.level"),
        FilterParam.factory(param="h-parent", field="hierarchy.parent"),
        FilterParam.factory(param="h-ancestor", field="hierarchy.ancestors"),
        FilterParam.factory(
            param="h-ancestor-or-self", field="hierarchy.ancestors_or_self"
        ),
    ] + InvenioVocabularySearchOptions.params_interpreters_cls

    sort_options = {
        **InvenioSearchOptions.sort_options,
    }

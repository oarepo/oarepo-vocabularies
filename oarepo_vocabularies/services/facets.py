from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels


class VocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, **kwargs):
        field = field + ".id"
        super().__init__(
            field=field, value_labels=VocabularyLabels(vocabulary), **kwargs
        )


class HierarchyVocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, **kwargs):
        field = field + ".hierarchy.ancestors_or_self"
        super().__init__(
            field=field, value_labels=VocabularyLabels(vocabulary), **kwargs
        )

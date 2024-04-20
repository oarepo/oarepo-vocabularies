from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels

from oarepo_vocabularies.proxies import current_ui_vocabulary_cache


class VocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, **kwargs):
        field = field + ".id"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary),
            **kwargs,
        )


class HierarchyVocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, **kwargs):
        field = field + ".hierarchy.ancestors_or_self"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary),
            **kwargs,
        )


class CachedVocabularyLabels(VocabularyLabels):
    _internal_vocabulary_terms_cache = None

    def __call__(self, ids):
        if not ids:
            return {}
        cache = current_ui_vocabulary_cache
        resolved = cache.resolve([(self.vocabulary, _id) for _id in ids])
        return {_id: resolved.get(_id)["title"] for _id in ids}

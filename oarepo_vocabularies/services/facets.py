import cachetools
from flask import current_app
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels


class VocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, *, use_cache=True, **kwargs):
        field = field + ".id"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary)
            if use_cache
            else VocabularyLabels(vocabulary),
            **kwargs,
        )


class HierarchyVocabularyFacet(TermsFacet):
    def __init__(self, vocabulary, field, *, use_cache=True, **kwargs):
        field = field + ".hierarchy.ancestors_or_self"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary)
            if use_cache
            else VocabularyLabels(vocabulary),
            **kwargs,
        )


class CachedVocabularyLabels(VocabularyLabels):
    _internal_vocabulary_terms_cache = None

    def __call__(self, ids):
        if not ids:
            return {}

        ret = {}
        to_fetch = []
        for _id in ids:
            cached = self.vocabulary_terms_cache.get((self.vocabulary, _id), None)
            if cached:
                ret[_id] = cached
            else:
                to_fetch.append(_id)
        if to_fetch:
            fetched = super().__call__(ids)
            for _id, v in fetched.items():
                self.vocabulary_terms_cache[(self.vocabulary, _id)] = v
            ret.update(fetched)
        return ret

    @property
    def vocabulary_terms_cache(self):
        # there might be a race condition resulting in cache created twice,
        # but no need to handle - just the first request will be inefficient
        if type(self)._internal_vocabulary_terms_cache:
            return self._internal_vocabulary_terms_cache
        vocabulary_cache_size = current_app.config.get(
            "VOCABULARIES_FACET_CACHE_SIZE", 2048
        )
        vocabulary_cache_ttl = current_app.config.get(
            "VOCABULARIES_FACET_CACHE_TTL", 60 * 24 * 24
        )
        cache = type(self)._internal_vocabulary_terms_cache = cachetools.TTLCache(
            maxsize=vocabulary_cache_size, ttl=vocabulary_cache_ttl
        )
        return cache

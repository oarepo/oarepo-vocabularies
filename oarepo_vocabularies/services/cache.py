import contextlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

import marshmallow
from cachetools import TTLCache
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from oarepo_runtime.i18n import get_locale

from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField


class VocabularyCacheItem:
    last_modified: datetime
    items: Dict[str, Any]

    def __init__(self):
        self.last_modified = datetime.fromtimestamp(0, timezone.utc)
        self.items = {}


class DepositI18nHierarchySchema(marshmallow.Schema):
    title = marshmallow.fields.List(VocabularyI18nStrUIField())
    ancestors = marshmallow.fields.List(marshmallow.fields.String())


class VocabularyPrefetchSchema(marshmallow.Schema):
    title = VocabularyI18nStrUIField(data_key="text")
    hierarchy = marshmallow.fields.Nested(
        DepositI18nHierarchySchema(), data_key="hierarchy"
    )
    props = marshmallow.fields.Dict(
        keys=marshmallow.fields.String(), values=marshmallow.fields.String()
    )
    tags = marshmallow.fields.List(marshmallow.fields.String())
    icon = marshmallow.fields.String()


class VocabularyCache:
    cache: Dict[str, Dict[str, VocabularyCacheItem]]
    """Language => vocabulary type => last modified + items"""
    lru_terms_cache = TTLCache(maxsize=10000, ttl=3600)

    count_from_cache = 0
    count_prefetched = 0
    count_fetched = 0

    def __init__(self):
        self.cache = {}

    @contextlib.contextmanager
    def language_cache(self, language):
        cached_language = {**self.cache.get(language, {})}

        yield cached_language
        self.cache[language] = cached_language

    def update(self, vocabulary_types: List[str]):
        if not vocabulary_types:
            return

        locale = get_locale()

        language = locale.language

        with self.language_cache(language) as cached_language:
            if not self._check_modified(cached_language, vocabulary_types):
                return

            by_vocabulary_type = {}
            max_modified = {}
            for item, dumped_item in self._serialize_items(
                locale, self._prefetch_vocabularies(vocabulary_types)
            ):
                by_vocabulary_type.setdefault(item["type"], {})[item["id"]] = (
                    dumped_item
                )
                if item["type"] not in max_modified:
                    max_modified[item["type"]] = datetime.fromtimestamp(0, timezone.utc)

                modified = datetime.fromisoformat(item["updated"])
                if max_modified[item["type"]] < modified:
                    max_modified[item["type"]] = modified

            if not by_vocabulary_type:
                return

            for vocab_type, items in by_vocabulary_type.items():
                if vocab_type not in cached_language:
                    cached_language[vocab_type] = VocabularyCacheItem()
                cached_language[vocab_type].items = items
                self.count_prefetched += len(items)
                cached_language[vocab_type].last_modified = max_modified[vocab_type]

    def clear(self):
        self.cache = {}
        self.lru_terms_cache = TTLCache(maxsize=10000, ttl=3600)
        self.count_from_cache = 0
        self.count_fetched = 0
        self.count_prefetched = 0

    def _prefetch_vocabularies(self, vocabulary_types: List[str]):
        yield from vocabulary_service.scan(
            system_identity,
            params={
                "type": vocabulary_types,
                "sort": "title",
                "size": 1000,
            },
            preserve_order=True,
        )

    def _check_modified(self, cached_language, vocabulary_types: List[str]):
        params = {
            "size": 1,
            "updated_after": {
                vt: (
                    cached_language[vt].last_modified.isoformat()
                    if vt in cached_language
                    else None
                )
                for vt in vocabulary_types
            },
        }

        result = vocabulary_service.search_many(
            system_identity,
            params=params,
        )
        return result.total > 0

    def _serialize_items(self, locale, items):
        schema = VocabularyPrefetchSchema(context={"locale": locale})

        for item in items:
            dumped_item = schema.dump(item)
            yield item, dumped_item

    def get(self, vocabulary_types: List[str]):
        self.update(vocabulary_types)
        language = get_locale().language
        ret = {}
        for vocabulary_type in vocabulary_types:
            ret[vocabulary_type] = self.cache[language][vocabulary_type].items
            self.count_from_cache += len(ret[vocabulary_type])

        return ret

    def resolve(self, ids):
        """
        Resolves vocabulary ids to their localized records.

        :param ids: list of vocabulary ids in the form of tuple (type, id)
        """
        locale = get_locale()
        language = locale.language

        # check if these are in the lru cache
        cached, uncached, uncached_small = self._split_cached_uncached(language, ids)

        self.count_from_cache += len(cached)
        self.count_prefetched += len(uncached_small)
        self.count_fetched += len(uncached)

        if uncached_small:
            self._fill_from_small_vocabularies_cache(language, uncached_small, cached)

        if uncached:
            for item, serialized_item in self._serialize_items(
                locale,
                vocabulary_service.search_many(
                    system_identity, params={"ids": uncached}
                ),
            ):
                typed_id = (item["type"], item["id"])
                cached[typed_id] = serialized_item
                self.lru_terms_cache[(language, typed_id)] = serialized_item

        return cached

    def _fill_from_small_vocabularies_cache(self, language, uncached_small, cached):
        # TODO: is there a performance improvement for uncached_small or should we treat all as uncached?
        self.update(list(uncached_small.keys()))
        cached_types = self.get(list(uncached_small.keys()))
        for vocab_type, items in uncached_small.items():
            for it in items:
                cached[(vocab_type, it)] = cached_types[vocab_type][it]
                self.lru_terms_cache[(language, (vocab_type, it))] = cached_types[
                    vocab_type
                ][it]

    def _split_cached_uncached(self, language, ids):
        cached = {}
        uncached = []
        uncached_small = defaultdict(list)
        with self.language_cache(language) as cached_language:
            for vocab_id in ids:
                term = self.lru_terms_cache.get((language, vocab_id))
                if term:
                    cached[vocab_id] = term
                else:
                    if vocab_id[0] in cached_language:
                        uncached_small[vocab_id[0]].append(vocab_id[1])
                    else:
                        uncached.append(vocab_id)
        return cached, uncached, uncached_small

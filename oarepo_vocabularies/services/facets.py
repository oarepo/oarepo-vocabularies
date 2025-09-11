#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Facets for vocabularies."""

from __future__ import annotations

from typing import Any

from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels

from oarepo_vocabularies.proxies import current_ui_vocabulary_cache


class VocabularyFacet(TermsFacet):
    """Facet for vocabulary."""

    def __init__(self, vocabulary: str, field: str, **kwargs: Any) -> None:
        """Initialize the VocabularyFacet."""
        field = field + ".id"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary),
            **kwargs,
        )


class HierarchyVocabularyFacet(TermsFacet):
    """Facet for vocabulary hierarchy."""

    def __init__(self, vocabulary: str, field: str, **kwargs: Any) -> None:
        """Initialize the HierarchyVocabularyFacet."""
        field = field + ".hierarchy.ancestors_or_self"
        super().__init__(
            field=field,
            value_labels=CachedVocabularyLabels(vocabulary),
            **kwargs,
        )


class CachedVocabularyLabels(VocabularyLabels):
    """Cached vocabulary labels."""

    _internal_vocabulary_terms_cache = None

    def _get_title(self, cache: Any, _id: str) -> dict | None:
        item = cache.get((self.vocabulary, _id))
        if item:
            return item["title"]
        return None

    def __call__(self, ids: list) -> dict:
        """Get labels for the given ids."""
        if not ids:
            return {}
        cache = current_ui_vocabulary_cache
        resolved = cache.resolve([(self.vocabulary, _id) for _id in ids], self.vocabulary)
        return {_id: self._get_title(resolved, _id) for _id in ids}

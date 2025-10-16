#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Search for oarepo-vocabularies."""

from __future__ import annotations

from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING, ClassVar

from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records import (
    SearchOptions as InvenioSearchOptions,
)
from invenio_records_resources.services.records.params import (
    FilterParam,
    ParamInterpreter,
)
from invenio_records_resources.services.records.queryparser import QueryParser
from opensearch_dsl import query
from opensearch_dsl.query import Bool, Range, Term, Terms

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.base import ServiceConfig
    from opensearch_dsl import Search

TYPE_ID_FIELD = "type.id"
ID_FIELD = "id"


class VocabularyQueryParser(QueryParser):
    """Parser for search queries."""

    def parse(self, query_str: str) -> query.Query:
        """Parse the query string, adding language-specific fields."""
        original_parsed_query = super().parse(query_str)
        current_locale = get_locale()
        if current_locale:
            language_conditions = [
                query.QueryString(
                    query=original_parsed_query.query,
                    fields=[f"hierarchy.title.{current_locale.language}"],
                    default_operator="AND",
                    boost=5,
                ),
                query.QueryString(
                    query=original_parsed_query.query,
                    fields=[f"title.{current_locale.language}"],
                    default_operator="AND",
                    boost=10,
                ),
            ]
            original_parsed_query = query.Bool(
                should=[original_parsed_query, *language_conditions],
                minimum_should_match=1,
            )

        return original_parsed_query


class SourceParam(ParamInterpreter):
    """Evaluate the 'q' or 'suggest' parameter."""

    def apply(self, identity: Identity, search: Search, params: dict) -> Search:  # noqa: ARG002 # type: ignore[override]
        """Apply the source parameter."""
        source = params.get("source")
        if not source:
            return search
        return search.source(source)


class UpdatedAfterParam(ParamInterpreter):
    """Evaluate type filter."""

    def __init__(self, param_name: str, field_name: str, config: ServiceConfig):
        """."""
        self.param_name = param_name
        self.field_name = field_name
        super().__init__(config)  # type: ignore[arg-type]

    @classmethod
    def factory(cls, param: str, field: str) -> partial[ParamInterpreter]:
        """Create a new filter parameter."""
        return partial(cls, param, field)

    def apply(self, identity: Identity, search: Search, params: dict) -> Search:  # noqa: ARG002 # type: ignore[override]
        """Apply a filter to get only records for a specific type."""
        # Pop because we don't want it to show up in links.
        # TODO: only pop if needed.
        value = params.pop(self.param_name, None)
        if value:
            vocabulary_filter = []
            for k, v in value.items():
                if v:
                    vocabulary_filter.append(
                        Bool(
                            must=[
                                Range(**{self.field_name: {"gt": v}}),  # type: ignore[arg-type]
                                Term(**{TYPE_ID_FIELD: k}),
                            ]
                        )
                    )
                else:
                    vocabulary_filter.append(Term(**{TYPE_ID_FIELD: k}))
            vocabulary_filter = Bool(should=vocabulary_filter, minimum_should_match=1)
            search = search.filter(vocabulary_filter)

        return search


class VocabularyIdsParam(ParamInterpreter):
    """Evaluate type filter."""

    def apply(self, identity: Identity, search: Search, params: dict) -> Search:  # noqa: ARG002 # type: ignore[override]
        """Apply a filter to get only records for a specific type."""
        ids = params.pop("ids", None)
        if not ids:
            return search
        # ids is a list of (vocabulary_type, vocabulary_id) tuples
        by_type = defaultdict(list)
        for vt, vid in ids:
            by_type[vt].append(vid)
        search_filters = []
        for vt, vids in by_type.items():
            search_filters.append(Bool(must=[Term(**{TYPE_ID_FIELD: vt}), Terms(**{ID_FIELD: vids})]))  # type: ignore[arg-type]
        return search.filter(Bool(should=search_filters, minimum_should_match=1))


class VocabularySearchOptions(InvenioSearchOptions):
    """Search options for vocabularies."""

    params_interpreters_cls: ClassVar[  # type: ignore[override]
        list[type[FilterParam | ParamInterpreter] | partial[FilterParam] | partial[ParamInterpreter]]
    ] = [
        FilterParam.factory(param="tags", field="tags"),
        UpdatedAfterParam.factory(param="updated_after", field="updated"),
        VocabularyIdsParam,
        FilterParam.factory(param="type", field=TYPE_ID_FIELD),
        FilterParam.factory(param="h-level", field="hierarchy.level"),
        FilterParam.factory(param="h-parent", field="hierarchy.parent"),
        FilterParam.factory(param="h-ancestor", field="hierarchy.ancestors"),
        FilterParam.factory(param="h-ancestor-or-self", field="hierarchy.ancestors_or_self"),
        SourceParam,
        *InvenioSearchOptions.params_interpreters_cls,
    ]
    query_parser_cls = VocabularyQueryParser

    extra_sort_options: ClassVar[dict[str, dict]] = {
        "bestmatch": {
            "title": _("Best match"),
            "fields": ["_score"],  # ES defaults to desc on `_score` field
        },
        "title": {
            "title": _("Title"),
            "fields": ["title_sort"],
        },
        "newest": {
            "title": _("Newest"),
            "fields": ["-created"],
        },
        "oldest": {
            "title": _("Oldest"),
            "fields": ["created"],
        },
    }

    # TODO: define sort_default_no_query to "title"
    # TODO: implement suggest_parser_cls
    # TODO: icu sort options

    facet_groups: ClassVar[dict[str, dict]] = {}

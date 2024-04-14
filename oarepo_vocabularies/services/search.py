from collections import defaultdict
from functools import partial

from invenio_records_resources.services.records.params import (
    FilterParam,
    ParamInterpreter,
)
from invenio_records_resources.services.records.queryparser import QueryParser
from oarepo_runtime.i18n import get_locale
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_runtime.services.search import (
    I18nSearchOptions,
    ICUSortOptions,
    ICUSuggestParser,
    SuggestField,
)
from opensearch_dsl import query
from opensearch_dsl.query import Bool, Range, Term, Terms

TYPE_ID_FIELD = "type.id"
ID_FIELD = "id"


class VocabularyQueryParser(QueryParser):
    def parse(self, query_str):
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

    def apply(self, identity, search, params):
        source = params.get("source")
        if not source:
            return search
        return search.source(source)


class UpdatedAfterParam(ParamInterpreter):
    """Evaluate type filter."""

    def __init__(self, param_name, field_name, config):
        """."""
        self.param_name = param_name
        self.field_name = field_name
        super().__init__(config)

    @classmethod
    def factory(cls, param=None, field=None):
        """Create a new filter parameter."""
        return partial(cls, param, field)

    def apply(self, identity, search, params):
        """Applies a filter to get only records for a specific type."""
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
                                Range(**{self.field_name: {"gt": v}}),
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
    def apply(self, identity, search, params):
        ids = params.pop("ids", None)
        if not ids:
            return search
        # ids is a list of (vocabulary_type, vocabulary_id) tuples
        by_type = defaultdict(list)
        for vt, vid in ids:
            by_type[vt].append(vid)
        search_filters = []
        for vt, vids in by_type.items():
            search_filters.append(
                Bool(must=[Term(**{TYPE_ID_FIELD: vt}), Terms(**{ID_FIELD: vids})])
            )
        return search.filter(Bool(should=search_filters, minimum_should_match=1))


class VocabularySearchOptions(I18nSearchOptions):
    SORT_CUSTOM_FIELD_NAME = "OAREPO_VOCABULARIES_SORT_CF"
    SUGGEST_CUSTOM_FIELD_NAME = "OAREPO_VOCABULARIES_SUGGEST_CF"

    params_interpreters_cls = [
        FilterParam.factory(param="tags", field="tags"),
        UpdatedAfterParam.factory(param="updated_after", field="updated"),
        VocabularyIdsParam,
        FilterParam.factory(param="type", field=TYPE_ID_FIELD),
        FilterParam.factory(param="h-level", field="hierarchy.level"),
        FilterParam.factory(param="h-parent", field="hierarchy.parent"),
        FilterParam.factory(param="h-ancestor", field="hierarchy.ancestors"),
        FilterParam.factory(
            param="h-ancestor-or-self", field="hierarchy.ancestors_or_self"
        ),
        SourceParam,
    ] + I18nSearchOptions.params_interpreters_cls

    query_parser_cls = VocabularyQueryParser

    extra_sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "title": dict(
            title=_("Title"),
            fields=["title_sort"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
    }

    sort_default = "bestmatch"
    sort_default_no_query = "title"

    sort_options = ICUSortOptions("vocabularies")
    suggest_parser_cls = ICUSuggestParser(
        "vocabularies",
        extra_fields=[SuggestField(field=ID_FIELD, boost=10, use_ngrams=False)],
    )

    # empty facet groups as we are inheriting from I18nSearchOptions
    facet_groups = {}

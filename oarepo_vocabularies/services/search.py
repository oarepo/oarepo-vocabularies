from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.params import (
    FilterParam,
    ParamInterpreter,
)
from invenio_records_resources.services.records.queryparser import QueryParser
from oarepo_runtime.services.search import (
    I18nSearchOptions,
    ICUSortOptions,
    ICUSuggestParser,
    SuggestField,
)
from opensearch_dsl import query

try:
    from invenio_i18n import get_locale
except ImportError:
    from invenio_i18n.babel import get_locale


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


class VocabularySearchOptions(I18nSearchOptions):
    SORT_CUSTOM_FIELD_NAME = "OAREPO_VOCABULARIES_SORT_CF"
    SUGGEST_CUSTOM_FIELD_NAME = "OAREPO_VOCABULARIES_SUGGEST_CF"

    params_interpreters_cls = [
        FilterParam.factory(param="tags", field="tags"),
        FilterParam.factory(param="type", field="type.id"),
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
        extra_fields=[SuggestField(field="id", boost=10, use_ngrams=False)],
    )

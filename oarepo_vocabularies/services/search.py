from flask import current_app
from invenio_records_resources.services.records.params import FilterParam
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_vocabularies.services.service import (
    VocabularySearchOptions as InvenioVocabularySearchOptions,
)
from opensearch_dsl import query
from sqlalchemy.util import classproperty

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


class VocabularySearchOptions(InvenioVocabularySearchOptions):
    params_interpreters_cls = [
        FilterParam.factory(param="h-level", field="hierarchy.level"),
        FilterParam.factory(param="h-parent", field="hierarchy.parent"),
        FilterParam.factory(param="h-ancestor", field="hierarchy.ancestors"),
        FilterParam.factory(
            param="h-ancestor-or-self", field="hierarchy.ancestors_or_self"
        ),
    ] + InvenioVocabularySearchOptions.params_interpreters_cls

    query_parser_cls = VocabularyQueryParser

    @classproperty
    def sort_options(clz):
        ret = super().sort_options
        # transform the sort options by the current language
        locale = get_locale()
        if not locale:
            return ret
        language = locale.language
        for cf in current_app.config["OAREPO_VOCABULARIES_SORT_CF"]:
            if cf.name == language:
                ret["title"]["fields"] = [f"sort.{cf.name}"]
                break
        return ret

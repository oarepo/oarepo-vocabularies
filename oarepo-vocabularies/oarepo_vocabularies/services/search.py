from elasticsearch_dsl import Q
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.params import ParamInterpreter, QueryStrParam, PaginationParam, \
    SortParam, FacetsParam
from invenio_vocabularies.services.service import VocabularySearchOptions

from oarepo_vocabularies.records.dumper import HierarchyPathExt


def _(x):
    """Identity function for string extraction."""
    return x


class HierarchyParam(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply the parameters."""
        hierarchy = params.get('hierarchy', None)
        if not hierarchy:
            return search
        conditions = []
        if 'level' in hierarchy:
            level = hierarchy['level']
            if isinstance(level, dict):
                conditions.append(Q(
                    'range',
                    **{f'{HierarchyPathExt.HIERARCHY_ATTR}.{HierarchyPathExt.HIERARCHY_LEVEL_ATTR}': level}
                ))
            else:
                conditions.append(Q(
                    'term',
                    **{f'{HierarchyPathExt.HIERARCHY_ATTR}.{HierarchyPathExt.HIERARCHY_LEVEL_ATTR}': level}
                ))
        if 'path' in hierarchy:
            conditions.append(Q(
                'term',
                **{f'{HierarchyPathExt.HIERARCHY_ATTR}.{HierarchyPathExt.HIERARCHY_PATH_ATTR}': hierarchy['path']}
            ))
        if 'reverse_path' in hierarchy:
            conditions.append(Q(
                'term',
                **{f'{HierarchyPathExt.HIERARCHY_ATTR}.{HierarchyPathExt.HIERARCHY_REVERSE_PATH_ATTR}': hierarchy[
                    'reverse_path']}
            ))
        if conditions:
            return search.filter(Q('bool', must=conditions))
        return search


class IDParam(ParamInterpreter):
    def apply(self, identity, search, params):
        ids = params.get('id', None)
        if not ids:
            return search
        return search.filter(Q('terms', id=ids))


class OptionalFacetsParam(FacetsParam):
    def apply(self, identity, search, params):
        if params.get('no_facets', False):
            return search
        return super().apply(identity, search, params)


class OARepoVocabulariesSearchOptionsBase(VocabularySearchOptions):
    sort_options = {
        # intentionally skip VocabularySearchOptions here - in basic, we do not have tags which are present on VSO
        **SearchOptions.sort_options,
        "title": dict(
            title=_("Title"),
            fields=["title_sort"],
        ),
        "id": dict(
            title=_("ID"),
            fields=["id"],
        ),
        "hierarchy_deepest": dict(
            title=_("ID desc"),
            fields=["-hierarchy.level"]
        ),
    }
    params_interpreters_cls = \
        [
            HierarchyParam,
            IDParam,
            QueryStrParam,
            PaginationParam,
            SortParam,
            OptionalFacetsParam
        ]

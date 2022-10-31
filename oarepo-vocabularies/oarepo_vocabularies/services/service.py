import uuid

from elasticsearch_dsl import Q, AttrDict
from invenio_pidstore.errors import PIDDoesNotExistError, ResolverError, PersistentIdentifierError
from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.records.results import RecordList
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services import VocabulariesService


class NoParentError(PersistentIdentifierError):
    """Parent for this vocabulary record does not exist."""

    def __init__(self, pid, *args, **kwargs):
        """Initialize exception."""
        self.pid = pid
        super(NoParentError, self).__init__(*args, **kwargs)


class OARepoVocabulariesServiceBase(VocabulariesService):
    def parent(self, identity, id_=None, **kwargs):
        """ID is a tuple (type, key)"""
        parent_id = self.record_cls.hierarchy_path.get_parent_id_from_id(id_)
        if parent_id:
            return self.read(identity=identity, id_=(id_[0], parent_id))
        else:
            raise NoParentError(id_)

    def ancestors(self, identity, id_=None, with_self=False, search_preference=None, **kwargs):
        prev = ''
        type_ = id_[0]
        id_ = id_[1]
        hierarchy_path = self.record_cls.hierarchy_path.get_from_id(id_)
        hierarchy_path = hierarchy_path.split('/')
        if not with_self:
            hierarchy_path = hierarchy_path[:-1]

        ancestor_hierarchy_paths = []
        for i in hierarchy_path:
            ancestor_hierarchy_paths.append(prev + i)
            prev += i + '/'
        params = {**kwargs}
        if 'sort' not in params:
            params['sort'] = 'hierarchy_deepest'
        if not ancestor_hierarchy_paths:
            return self._hierarchy_search_no_result(identity, type_, id_, params, kwargs,
                                                    'self+ancestors' if with_self else 'ancestors')
        params['id'] = self.record_cls.hierarchy_path.paths_to_id(ancestor_hierarchy_paths)
        params['no_facets'] = True

        return self._hierarchy_search(identity, type_, id_, params, kwargs, search_preference,
                                      'self+ancestors' if with_self else 'ancestors')

    def _hierarchy_search_no_result(self, identity, type_, id_, params, kwargs, hierarchy_type):
        vocabulary_type = VocabularyType.query.filter_by(id=type_).one()
        no_result = AttrDict({
            'hits': {
                'hits': [],
                'total': {
                    'value': 0
                }
            }
        })
        return self.result_list(
            self,
            identity,
            no_result,
            params,
            links_item_tpl=self.links_item_tpl,
            links_tpl=LinksTemplate(
                self.config.links_hierarchy,
                context={
                    "args": {
                        **kwargs,
                        "hierarchy": hierarchy_type
                    },
                    "type": vocabulary_type.id,
                    "id": id_
                },
            ),
        )

    def _hierarchy_search(self, identity, type_, id_, params, kwargs, search_preference, hierarchy_type):
        self.require_permission(identity, "search")

        vocabulary_type = VocabularyType.query.filter_by(id=type_).one()
        # Prepare and execute the search
        search_result = self._search(
            "search",
            identity,
            params,
            search_preference=search_preference,
            extra_filter=Q("term", type__id=vocabulary_type.id),
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_item_tpl=self.links_item_tpl,
            links_tpl=LinksTemplate(
                self.config.links_hierarchy,
                context={
                    "args": {
                        **kwargs,
                        "hierarchy": hierarchy_type
                    },
                    "type": vocabulary_type.id,
                    "id": id_
                },
            ),
        )

    def children(self, identity, id_=None, with_self=False, search_preference=None, **kwargs):
        record = self.record_cls.pid.resolve(id_)
        params = {**kwargs}
        if 'sort' not in params:
            params['sort'] = 'id'
        params['hierarchy'] = {
            'level': {
                'gte': record.level + (0 if with_self else 1),
                'lte': record.level + 1,
            },
            'path': record.hierarchy_path
        }
        params['no_facets'] = True

        return self._hierarchy_search(identity, id_[0], id_[1], params, kwargs, search_preference,
                                      'self+children' if with_self else 'children')

    def descendants(self, identity, id_=None, with_self=False, search_preference=None, **kwargs):
        params = {**kwargs}
        if 'sort' not in params:
            params['sort'] = 'id'
        record = self.record_cls.pid.resolve(id_)
        params['hierarchy'] = {
            'level': {'gte': record.level + (0 if with_self else 1)},
            'path': record.hierarchy_path
        }
        params['no_facets'] = True

        return self._hierarchy_search(identity, id_[0], id_[1], params, kwargs, search_preference,
                                      'self+descendants' if with_self else 'descendants')

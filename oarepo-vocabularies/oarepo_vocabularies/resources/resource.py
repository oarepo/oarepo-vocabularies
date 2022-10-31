from flask import g, abort
from flask_resources import response_handler, resource_requestctx, route, request_parser, from_conf
from invenio_records_resources.resources.records.resource import request_view_args, request_data
from invenio_records_resources.resources.records.utils import search_preference
from invenio_vocabularies.resources.resource import VocabulariesResource
from marshmallow import ValidationError
from flask_babelex import lazy_gettext as _

from oarepo_vocabularies.services.service import OARepoVocabulariesServiceBase


class InconsistentVocabularyTypeException(Exception):
    pass


request_hierarchy_args = request_parser(from_conf("request_hierarchy_args"), location="args")


class OARepoVocabulariesResourceBase(VocabulariesResource):
    service: OARepoVocabulariesServiceBase

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        rules = super().create_url_rules()
        rules.extend([
            route("POST", routes["vocabularies"], self.create_outside_vocabulary),
            route("POST", routes["item"], self.create_subterm),
        ])
        return rules

    @request_hierarchy_args
    def read(self):
        if 'hierarchy' in resource_requestctx.args:
            # hierarchy get
            hierarchy_op = resource_requestctx.args['hierarchy']
            if hierarchy_op == 'ancestors':
                return self.ancestors(with_self=False)
            elif hierarchy_op in ('self+ancestors', 'self ancestors'):
                return self.ancestors(with_self=True)
            elif hierarchy_op == 'children':
                return self.children(with_self=False)
            elif hierarchy_op in ('self+children', 'self children'):
                return self.children(with_self=True)
            elif hierarchy_op == 'descendants':
                return self.descendants(with_self=False)
            elif hierarchy_op in ('self+descendants', 'self descendants'):
                return self.descendants(with_self=True)
            else:
                abort(400, 'Bad hierarchy operation. Only "ancestors", "self+ancestors", '
                           '"children", "self+children", "descendants", "self+descendants" are allowed. '
                           '+ is either url space escape or real +.')

        return super().read()

    @request_view_args
    @request_data
    @response_handler()
    def ancestors(self, with_self=False):
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        item = self.service.ancestors(g.identity, pid_value, with_self=with_self, search_preference=search_preference())
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def descendants(self, with_self=False):
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        item = self.service.descendants(g.identity, pid_value, with_self=with_self, search_preference=search_preference())
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def children(self, with_self=False):
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        item = self.service.children(g.identity, pid_value, with_self=with_self, search_preference=search_preference())
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def create(self):
        return self._create()

    def _create(self):
        type_ = resource_requestctx.view_args["type"]
        if 'type' not in resource_requestctx.data:
            resource_requestctx.data['type'] = type_
        elif resource_requestctx.data['type'] != type_:
            raise InconsistentVocabularyTypeException()

        item = self.service.create(
            g.identity,
            resource_requestctx.data or {},
        )
        return item.to_dict(), 201

    def _set_type(self, type_):
        if 'type' not in resource_requestctx.data:
            resource_requestctx.data['type'] = type_
        elif resource_requestctx.data['type'] != type_:
            raise InconsistentVocabularyTypeException()

    @request_view_args
    @request_data
    @response_handler()
    def create_subterm(self):
        type_ = resource_requestctx.view_args["type"]
        pid_value = resource_requestctx.view_args['pid_value']
        if pid_value.endswith('/'):
            pid_value = pid_value[:-1]
        parent = self.service.read(g.identity, (type_, pid_value))
        resource_requestctx.data['id'] = parent['id'] + '/' + resource_requestctx.data['id']
        return self._create()

    @request_data
    @response_handler()
    def create_outside_vocabulary(self):
        if 'type' not in resource_requestctx.data:
            raise ValidationError(
                _("Vocabulary type missing in data")
            )

        item = self.service.create(
            g.identity,
            resource_requestctx.data or {},
        )
        return item.to_dict(), 201

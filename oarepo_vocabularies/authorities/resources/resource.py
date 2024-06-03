from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.pagination import Pagination
from invenio_records_resources.services import LinksTemplate

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.resources.records.resource import (
    request_search_args,
    request_view_args,
)
from invenio_vocabularies.records.models import VocabularyType

from oarepo_vocabularies.authorities.proxies import authorities
from oarepo_vocabularies.authorities.providers import AuthorityProvider
from oarepo_vocabularies.ui.resources.resource import request_vocabulary_args


class AuthoritativeVocabulariesResource(Resource):
    def __init__(self, config):
        super().__init__(config)

    def create_url_rules(self):
        routes = self.config.routes

        return [route("GET", routes["list"], self.list)]

    @request_search_args
    @request_view_args
    @request_vocabulary_args
    @response_handler()
    def list(self):
        identity = g.identity
        authority_provider: AuthorityProvider = authorities.get_authority_api(
            resource_requestctx.view_args["vocabulary_type"]
        )
        vocabulary_type = VocabularyType.query.filter_by(
            id=resource_requestctx.view_args["vocabulary_type"]
        ).one()
        if not authority_provider:
            return "No authority provider.", 404

        # Get hits from authority.
        params = resource_requestctx.args
        items, total, page_size = authority_provider.search(identity, params)

        pagination = Pagination(
            params.get("size", 10),
            params.get("page", 1),
            total,
        )
        links = self.expand_search_links(
            identity,
            pagination,
            resource_requestctx.args,
            resource_requestctx.view_args,
        )

        results = {"hits": {"hits": items, "total": total}, "links": links}

        # Mark external, resolve uuid.
        ids = [item["id"] for item in results["hits"]["hits"]]

        internal_query = db.session.query(PersistentIdentifier.pid_value).filter(
            db.and_(
                PersistentIdentifier.pid_type == vocabulary_type.pid_type,
                PersistentIdentifier.pid_value.in_(ids),
            )
        )
        query_results = {row.pid_value for row in internal_query}

        for item in results["hits"]["hits"]:
            auth_id = item["id"]
            item.setdefault("props", {})["external"] = auth_id not in query_results

        return results, 200

    def expand_search_links(self, identity, pagination, args, view_args):
        """Get links for this result item."""

        tpl = LinksTemplate(
            self.config.ui_links_search,
            {
                "config": self.config,
                "url_prefix": self.config.url_prefix,
                "args": args,
                "vocabulary_type": view_args["vocabulary_type"],
            },
        )
        return tpl.expand(identity, pagination)

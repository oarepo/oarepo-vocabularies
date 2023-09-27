from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.resources.records.resource import (
    request_search_args,
    request_view_args,
)
from invenio_vocabularies.records.models import VocabularyType

from oarepo_vocabularies.authorities.proxies import authorities
from oarepo_vocabularies.authorities.service import AuthorityService


class AuthoritativeVocabulariesResource(Resource):
    def __init__(self, config):
        super().__init__(config)

    def create_url_rules(self):
        routes = self.config.routes

        return [route("GET", routes["list"], self.list)]

    @request_search_args
    @request_view_args
    @response_handler()
    def list(self):
        authority_service: AuthorityService = authorities.get_authority_api(
            resource_requestctx.view_args["type"]
        )
        vocabulary_type = VocabularyType.query.filter_by(
            id=resource_requestctx.view_args["type"]
        ).one()
        if not authority_service:
            return "No authority getter.", 404

        # Get hits from authority.
        params = resource_requestctx.args
        q, page, size = params["q"], params["page"], params["size"]
        results = authority_service.search(query=q, page=page, size=size)

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

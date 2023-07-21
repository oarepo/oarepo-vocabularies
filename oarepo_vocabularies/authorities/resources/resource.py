from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.resources.records.resource import (
    request_search_args,
    request_view_args,
)
from sqlalchemy.orm import aliased

from oarepo_vocabularies.authorities.proxies import current_vocabularies_authorities


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
        auth_getter = current_vocabularies_authorities(
            resource_requestctx.view_args["type"]
        )
        if not auth_getter:
            return "No authority getter.", 404

        # Get hits from authority.
        params = resource_requestctx.args
        q, page, size = params["q"], params["page"], params["size"]
        results = auth_getter(q, page, size)

        # Mark external, resolve uuid.
        authoritative_ids = [item["props"]["authoritative_id"] for item in results]

        authvc = db.session.query(
            PersistentIdentifier.pid_value, PersistentIdentifier.object_uuid
        ).filter(
            db.and_(
                PersistentIdentifier.pid_type == "authvc",
                PersistentIdentifier.pid_value.in_(authoritative_ids),
            )
        )

        PersistentIdentifierAlias = aliased(PersistentIdentifier)
        query = authvc.join(
            PersistentIdentifierAlias,
            PersistentIdentifier.object_uuid == PersistentIdentifierAlias.object_uuid,
        )

        query_results = query.all()
        query_results = {row.pid_value: row.object_uuid for row in query_results}

        authority_results = []
        for item in results:
            auth_id = item["props"]["authoritative_id"]

            if auth_id not in query_results:
                item["props"]["external"] = True
                authority_results.append(item)
                continue

            uuid = query_results[auth_id]
            item["props"]["external"] = uuid is None
            item["props"]["uuid"] = uuid
            authority_results.append(item)

        result = {"hits": {"hits": authority_results}}
        return result, 200

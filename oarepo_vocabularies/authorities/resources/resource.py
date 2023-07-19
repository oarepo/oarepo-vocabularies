from flask_resources import (
    Resource,
    response_handler,
    route,
    resource_requestctx
)
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.resources.records.resource import request_search_args

from oarepo_vocabularies.authorities.proxies import current_vocabularies_authorities

class AuthoritativeVocabulariesResource(Resource):
    def __init__(self, config):
        super().__init__(config)
        
    def create_url_rules(self):
        routes = self.config.routes
        
        return [route("GET", routes["list"], self.list)]
    
    @request_search_args
    @response_handler(many=True)
    def list(self, vocabulary_type: str):
        auth_getter = current_vocabularies_authorities(vocabulary_type)
        if not auth_getter:
            return "No authority getter.", 404
        
        # Get hits from authority.
        params = resource_requestctx.args
        q, page, size = params.q, params.page, params.size
        results = auth_getter(q, page, size)
    
        # Mark external, resolve uuid.
        authoritative_ids = [item.properties["authoritative_id"] for item in results]
        
        subquery = db.session.query(
            PersistentIdentifier.pid_value,
            PersistentIdentifier.object_uuid
        ).filter(
            db.and_(
                PersistentIdentifier.pid_type == "authvc",
                PersistentIdentifier.pid_value.in_(authoritative_ids)
            )
        ).subquery('sub')
        
        query = db.session.query(
            subquery.c.pid_value,
            subquery.c.object_uuid
        ).join(
            subquery,
            db.and_(
                PersistentIdentifier.pid_type == "id",
                PersistentIdentifier.object_uuid == subquery.c.object_uuid,
            ),
            isouter=True
        ).all()
        query_results = {row.pid_value:row.object_uuid for row in query}
        
        authority_results = []
        for item in results:
            auth_id = item.properties["authoritative_id"]
            uuid = query_results[auth_id]
            
            item['external'] = uuid is None
            item['id'] = uuid

        result = {
            "hits": {
                "hits": authority_results
            }
        }
        return result, 200
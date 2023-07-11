from flask_resources import (
    Resource,
    response_handler,
    route,
    resource_requestctx
)
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.resources.records.resource import request_search_args
from sqlalchemy import select

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
    
        # Filter authority results if such PID already exists in our database.
        authority_unique_results = []
        for item in results:
            id = item.props.authoritative_id
            stmt = select(PersistentIdentifier).where(PersistentIdentifier.pid_value == id)
            result = db.session.execute(stmt).first()
            
            if not result:
                authority_unique_results.append(item)
        
        result = {
            "hits": {
                "hits": authority_unique_results
            }
        }
        return result, 200
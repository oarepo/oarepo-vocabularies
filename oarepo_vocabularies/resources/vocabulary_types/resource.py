from flask import g
from flask_resources import (
    Resource,
    route,
    response_handler
)

class VocabularyTypeResource(Resource):
    def create_url_rules(self):
        routes = self.config.routes
        
        return [
            route("GET", routes["list"], self.list)
        ]
    
    @response_handler(many=True)
    def list(self):
        """Perform a search over the items."""
        identity = g.identity
        hits = self.service.search(identity=identity)
        return hits.to_dict(), 200
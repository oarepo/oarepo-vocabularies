import logging
import os
from flask import current_app
import requests

from oarepo_vocabularies.authorities.providers.base import AuthorityProvider


logger = logging.getLogger("oarepo-vocabularies.providers.openaire")

class OpenAIREClient(object):
    
    def __init__(self, client_id, client_secret, url=None, testing=False, timeout=None, **kwargs):
        self.api_url = url or "google.com"
        self.testing = testing
        if self.testing:
            self.api_url = "test.com"
        
        self.timeout = timeout or 10000
        
    
class OpenAIREProvider(AuthorityProvider):
    
    def __init__(self, url=None, testing=False, **kwargs):
        try:
            client_id = current_app.config["OPENAIRE_CLIENT_ID"]
            client_secret = current_app.config["OPENAIRE_CLIENT_SECRET"]
        except RuntimeError:
            client_id = os.environ["INVENIO_OPENAIRE_CLIENT_ID"]
            client_secret = os.environ["INVENIO_OPENAIRE_CLIENT_SECRET"]
        except KeyError:
            raise KeyError("OPENAIRE_CLIENT_ID and OPENAIRE_CLIENT_SECRET must be set in the configuration or as environment variables.")
        self.openaire_client = OpenAIREClient(client_id, client_secret, url, testing, **kwargs)
        
    def search(self, identity, params, **kwargs):
        return super().search(identity, params, **kwargs)
    
    def get(self, identity, item_id, *, uow, value, **kwargs):
        return super().get(identity, item_id, uow=uow, value=value, **kwargs)
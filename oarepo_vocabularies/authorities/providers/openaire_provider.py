
from oarepo_vocabularies.authorities.providers.base import AuthorityProvider


class OpenAIREClient(object):
    
    def __init__(self):
        pass
        
    
class OpenAIREProvider(AuthorityProvider):
    
    def __init__(self):
        self.openaire_client = OpenAIREClient() 
        
    def search(self, identity, params, **kwargs):
        return super().search(identity, params, **kwargs)
    
    def get(self, identity, item_id, *, uow, value, **kwargs):
        return super().get(identity, item_id, uow=uow, value=value, **kwargs)
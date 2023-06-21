from invenio_records_resources.services import (
    LinksTemplate,
    pagination_links   
)
from invenio_records_resources.services.base import Service

class VocabulariesService(Service):
    """Vocabulary service."""
    
    def search(
        self, identity, params=None, search_preference=None, **kwargs
    ):
        """Search for vocabulary entries."""
        self.require_permission(identity, "list_vocabularies")
        
        # Prepare and execute the search.
        params = params or {}
        search_result = self._search(
            "search",
            identity,
            params,
            search_preference,
            **kwargs
        ).execute()
        
        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                pagination_links("{+api}/vocabularies{?args*}"),    # NOTE: only because of coherence
                context={ "args": params }
            ),
            links_item_tpl=self.config.vocabularies_listing_item
        )
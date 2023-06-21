from invenio_records_resources.services import (
    LinksTemplate,
    pagination_links   
)
from invenio_records_resources.services.base import Service
from invenio_vocabularies.records.api import VocabularyType

class VocabulariesService(Service):
    """Vocabulary service."""
    
    def search(self, identity):
        """Search for vocabulary entries."""
        self.require_permission(identity, "can_list_vocabularies")
        
        vocabulary_types = VocabularyType.query.all()
        
        # Enrich vocab types with config values.
        
        return self.result_list(
            self,
            identity,
            links_tpl=LinksTemplate(pagination_links("{+api}/vocabularies")),
            links_item_tpl=self.config.vocabularies_listing_item
        )
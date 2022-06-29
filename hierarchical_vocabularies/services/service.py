from invenio_records_resources.services import RecordService
from invenio_vocabularies.services.service import (
    VocabulariesService,
    VocabulariesServiceConfig,
)

from ..records.api import HVocabulary

# from .components import PIDHierarchyComponent
from .schema import HVocabularySchema


class HVocabulariesServiceConfig(VocabulariesServiceConfig):
    """Hierarchical vocabulary service configuration."""

    record_cls = HVocabulary
    schema = HVocabularySchema


class HVocabulariesService(VocabulariesService):
    """Hierarchical vocabulary service."""

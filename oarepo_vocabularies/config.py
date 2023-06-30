from invenio_records_resources.services.custom_fields.text import KeywordCF

from oarepo_vocabularies.fixtures import (
    VocabularyReader,
    VocabularyWriter,
    vocabularies_generator,
)
from oarepo_vocabularies.services.config import VocabularyTypeServiceConfig
from oarepo_vocabularies.services.custom_fields import hierarchy
from oarepo_vocabularies.services.service import VocabularyTypeService

# NOTE: Example.
INVENIO_VOCABULARY_TYPE_METADATA = {
    "languages": {
        "name": {
            "cs": "jazyky",
            "en": "languages",
        },
        "description": {
            "cs": "slovnikovy typ ceskeho jazyka.",
            "en": "czech language vocabulary type.",
        },
    },
    "licences": {
        "name": {
            "cs": "licence",
            "en": "licences",
        },
        "description": {
            "cs": "slovnikovy typ licencii.",
            "en": "lincenses vocabulary type.",
        },
    },
}

OAREPO_VOCABULARIES_HIERARCHY_CF = [
    hierarchy.HierarchyLevelCF("level"),
    hierarchy.HierarchyTitleCF("title"),
    hierarchy.HierarchyAncestorsCF("ancestors", multiple=True),
    hierarchy.HierarchyAncestorsOrSelfCF("ancestors_or_self", multiple=True),
    KeywordCF("parent"),
]


OAREPO_VOCABULARIES_CUSTOM_CF = []

VOCABULARY_TYPE_SERVICE = VocabularyTypeService
VOCABULARY_TYPE_SERVICE_CONFIG = VocabularyTypeServiceConfig

DATASTREAMS_CONFIG_GENERATOR_VOCABULARIES = vocabularies_generator

DEFAULT_DATASTREAMS_READERS = {"vocabulary": VocabularyReader}

DEFAULT_DATASTREAMS_WRITERS = {"vocabulary": VocabularyWriter}

VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 24 * 24

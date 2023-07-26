from invenio_records_resources.services.custom_fields.text import KeywordCF

from oarepo_vocabularies.fixtures import (
    VocabularyReader,
    VocabularyWriter,
    vocabularies_generator,
)
from oarepo_vocabularies.resources.vocabulary_type import (
    VocabularyTypeResource,
    VocabularyTypeResourceConfig,
)
from oarepo_vocabularies.services.config import VocabularyTypeServiceConfig
from oarepo_vocabularies.services.custom_fields import hierarchy
from oarepo_vocabularies.services.service import VocabularyTypeService

INVENIO_VOCABULARY_TYPE_METADATA = {
    # etc.
    # "affilliations": {
    #    "authority": {
    #        "name": "ROR",
    #        "url": "https://api.ror.org/organizations",
    #        "getter": lambda q, page, size: True
    #    }
    # },
    # "grants": {
    #    "authority": {
    #        "name": "Openaire",
    #        "url": "https://api.openaire.eu/search/projects",
    #        "getter": lambda q, page, size: True
    #    }
    # },
    # "languages": {
    #     "name": {
    #         "cs": "jazyky",
    #         "en": "languages",
    #     },
    #     "description": {
    #         "cs": "slovnikovy typ ceskeho jazyka.",
    #         "en": "czech language vocabulary type.",
    #     },
    #     "hierarchical": False,
    #     "props": {...}
    # },
    # "organisms": {
    #    "authority": {
    #        "name": "NCBI",
    #        "url": "https://ncbi.nlm.nih.gov/",
    #        "getter": lambda q, page, size: True
    #    }
    # }
}

OAREPO_VOCABULARIES_HIERARCHY_CF = [
    hierarchy.HierarchyLevelCF("level"),
    hierarchy.HierarchyTitleCF("title"),
    hierarchy.HierarchyAncestorsCF("ancestors", multiple=True),
    hierarchy.HierarchyAncestorsOrSelfCF("ancestors_or_self", multiple=True),
    KeywordCF("parent"),
]


OAREPO_VOCABULARIES_CUSTOM_CF = []

OAREPO_VOCABULARY_TYPE_SERVICE = VocabularyTypeService
OAREPO_VOCABULARY_TYPE_SERVICE_CONFIG = VocabularyTypeServiceConfig

OAREPO_VOCABULARY_TYPE_RESOURCE = VocabularyTypeResource
OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG = VocabularyTypeResourceConfig

DATASTREAMS_CONFIG_GENERATOR_VOCABULARIES = vocabularies_generator

DEFAULT_DATASTREAMS_READERS = {"vocabulary": VocabularyReader}

DEFAULT_DATASTREAMS_WRITERS = {"vocabulary": VocabularyWriter}

VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 24 * 24

# List of commonly used language vocabulary ids (for multilingual select inputs)
# MULTILINGUAL_COMMON_LANGUAGES = ["en", "cs", "sk", "de", "fr"]

# Completely disables usage of languages vocabulary in forms
# MULTILINGUAL_DISABLED = False

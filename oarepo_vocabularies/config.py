from invenio_records_resources.services.custom_fields.text import KeywordCF

from oarepo_vocabularies.fixtures import (
    AffiliationsWriter,
    AwardsWriter,
    NamesWriter,
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
from oarepo_vocabularies.services.permissions import VocabulariesPermissionPolicy
from oarepo_vocabularies.services.service import VocabularyTypeService

OAREPO_VOCABULARIES_PERMISSIONS_PRESETS = {"vocabularies": VocabulariesPermissionPolicy}

INVENIO_VOCABULARY_TYPE_METADATA = {
    # etc.
    # "affilliations": {
    #    "authority": <authority service class>
    # },
    # "grants": {
    #    "authority": <authority service class>
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
    #     "props": {"alpha3CodeNative": {
    #                 "description": _("ISO 639-2 standard 3-letter language code"),
    #                 "icon": None,
    #                 "label": _("Alpha3 code (native)"),
    #                 "multiple": False,
    #                 "options": [],
    #                 "placeholder": "eng, ces...",
    #             }},
    #     "custom_fields": ["names of custom fields from VOCABULARIES_CF to show in ui/serialize"],
    #     "dump_options": True
    # },
    # "organisms": {
    #    "authority": <authority service class>
    # }
}

OAREPO_VOCABULARIES_HIERARCHY_CF = [
    hierarchy.HierarchyLevelCF("level"),
    hierarchy.HierarchyTitleCF("title"),
    hierarchy.HierarchyAncestorsCF("ancestors", multiple=True),
    hierarchy.HierarchyAncestorsOrSelfCF("ancestors_or_self", multiple=True),
    hierarchy.HierarchyLeafCF("leaf"),
    KeywordCF("parent"),
]

OAREPO_VOCABULARIES_SORT_CF = []

OAREPO_VOCABULARIES_SUGGEST_CF = []

VOCABULARIES_CF = []

OAREPO_VOCABULARY_TYPE_SERVICE = VocabularyTypeService
OAREPO_VOCABULARY_TYPE_SERVICE_CONFIG = VocabularyTypeServiceConfig

OAREPO_VOCABULARY_TYPE_RESOURCE = VocabularyTypeResource
OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG = VocabularyTypeResourceConfig

DATASTREAMS_CONFIG_GENERATOR_VOCABULARIES = vocabularies_generator

DATASTREAMS_READERS = {"vocabulary": VocabularyReader}

DATASTREAMS_WRITERS = {
    "vocabulary": VocabularyWriter,
    "awards": AwardsWriter,
    "names": NamesWriter,
    "affiliations": AffiliationsWriter,
}

OAREPO_SPECIALIZED_VOCABULARIES_METADATA = {
    "awards": {
        "name": {"en": "Awards", "cs": "Granty"},
        "description": {"en": "Vocabulary of awards.", "cs": "Slovník grantů."},
    },
    "affiliations": {
        "name": {"en": "Affiliations", "cs": "Instituce"},
        "description": {
            "en": "Vocabulary of affiliations.",
            "cs": "Slovník institucí.",
        },
    },
    "names": {
        "name": {"en": "Names", "cs": "Jména"},
        "description": {"en": "Vocabulary of names.", "cs": "Slovník jmen."},
    },
    "funders": {
        "name": {"en": "Funders", "cs": "Poskytovatelé financí"},
        "description": {
            "en": "Vocabulary of funders.",
            "cs": "Slovník poskytovatelů financí.",
        },
    },
}

VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 24 * 24

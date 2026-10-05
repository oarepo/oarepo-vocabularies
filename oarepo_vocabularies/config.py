# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""oarepo_vocabularies configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_vocabularies.services.permissions import PermissionPolicy

from oarepo_vocabularies.resources.vocabulary_type import (
    VocabularyTypeResource,
    VocabularyTypeResourceConfig,
)
from oarepo_vocabularies.services.config import VocabularyTypeServiceConfig
from oarepo_vocabularies.services.service import VocabularyTypeService

if TYPE_CHECKING:
    from invenio_records_resources.services.custom_fields import BaseCF

OAREPO_VOCABULARIES_PERMISSIONS_PRESETS = {"vocabularies": PermissionPolicy}

INVENIO_VOCABULARY_TYPE_METADATA: dict[str, dict[str, Any]] = {}

OAREPO_VOCABULARIES_SORT_CF: list[str] = []

OAREPO_VOCABULARIES_SUGGEST_CF: list[str] = []

VOCABULARIES_CF: list[type[BaseCF]] = []

OAREPO_VOCABULARY_TYPE_SERVICE = VocabularyTypeService
OAREPO_VOCABULARY_TYPE_SERVICE_CONFIG = VocabularyTypeServiceConfig

OAREPO_VOCABULARY_TYPE_RESOURCE = VocabularyTypeResource
OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG = VocabularyTypeResourceConfig

OAREPO_VOCABULARY_NAMESPACE_URI: str | None = None
"""The namespace URI which is used in RDF export for icon and props."""

VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 24 * 24

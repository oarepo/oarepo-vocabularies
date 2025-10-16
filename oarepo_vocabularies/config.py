#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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


VOCABULARIES_FACET_CACHE_SIZE = 2048
VOCABULARIES_FACET_CACHE_TTL = 60 * 24 * 24

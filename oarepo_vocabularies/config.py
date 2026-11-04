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

OAREPO_VOCABULARIES_ORCID_DUMP_COLLECTION_ID = 7931102
"""Figshare collection holding the ORCID annual public data files."""

OAREPO_VOCABULARIES_ORCID_DUMP_GROUP_ID = 8907
"""Figshare group of ORCID.

A released data file lives in the group before (or without) being added to the
collection, so the group is searched as well.
"""

OAREPO_VOCABULARIES_ORCID_DUMP_API_URL = "https://api.figshare.com/v2"
"""Base url of the Figshare API used to discover the data file."""

OAREPO_VOCABULARIES_ORCID_DUMP_YEAR: int | None = None
"""Year of the ORCID public data file to import.

Pinning the year keeps the import reproducible: the same archive and checksum are used
on every run, and a newer release published by ORCID does not silently change what gets
loaded. Set to `None` to always import the newest file available in the collection.
"""

OAREPO_VOCABULARIES_ORCID_ROR_API_URL = "https://api.ror.org/v2"
"""ROR API used to import affiliations referenced by ORCID records but missing locally."""

OAREPO_VOCABULARIES_ORCID_ROR_CLIENT_ID: str | None = None
"""ROR API client id, sent as the ``Client-Id`` header.

Requests without a client id get a much lower rate limit from ROR. On a rate limit the
import waits (``Retry-After``, or a minute) and retries.
"""

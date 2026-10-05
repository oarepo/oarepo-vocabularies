# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Vocabulary type resource and its configuration."""

from __future__ import annotations

from oarepo_vocabularies.resources.vocabulary_type.config import (
    VocabularyTypeResourceConfig,
)
from oarepo_vocabularies.resources.vocabulary_type.resource import (
    VocabularyTypeResource,
)

__all__ = ("VocabularyTypeResource", "VocabularyTypeResourceConfig")

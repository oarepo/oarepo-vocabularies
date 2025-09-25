#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabulary type resource and its configuration."""

from __future__ import annotations

from oarepo_vocabularies.resources.vocabulary_type.config import (
    VocabularyTypeResourceConfig,
)
from oarepo_vocabularies.resources.vocabulary_type.resource import (
    VocabularyTypeResource,
)

__all__ = ("VocabularyTypeResource", "VocabularyTypeResourceConfig")

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI configuration for oarepo-vocabularies."""

from __future__ import annotations

OAREPO_VOCABULARIES_UI_RESOURCE = "oarepo_vocabularies.ui.resources.resource:InvenioVocabulariesUIResource"
OAREPO_VOCABULARIES_UI_RESOURCE_CONFIG = "oarepo_vocabularies.ui.resources.config:InvenioVocabulariesUIResourceConfig"

VOCABULARY_TYPE_UI_RESOURCE = "oarepo_vocabularies.ui.resources.vocabulary_type.resource:VocabularyTypeUIResource"

VOCABULARY_TYPE_UI_RESOURCE_CONFIG = (
    "oarepo_vocabularies.ui.resources.vocabulary_type.config:VocabularyTypeUIResourceConfig"
)
OAREPO_UI_LESS_COMPONENTS = [
    "dl_table",
]

# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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

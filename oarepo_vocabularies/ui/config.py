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

# templates of the vocabulary item detail page sidebar widgets, rendered in this order
OAREPO_VOCABULARIES_UI_SIDEBAR_TEMPLATES = [
    "oarepo_vocabularies_ui/record_detail/side_bar/manage.html",
    "oarepo_vocabularies_ui/record_detail/side_bar/export.html",
    "oarepo_vocabularies_ui/record_detail/side_bar/technical_metadata.html",
]

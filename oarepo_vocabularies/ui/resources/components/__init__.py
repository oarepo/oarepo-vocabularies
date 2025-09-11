#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI resource components for vocabularies."""

from .deposit import DepositVocabularyOptionsComponent
from .search import VocabularySearchComponent
from .vocabulary_ui_resource import VocabularyRecordsComponent

__all__ = (
    "DepositVocabularyOptionsComponent",
    "VocabularyRecordsComponent",
    "VocabularySearchComponent",
)

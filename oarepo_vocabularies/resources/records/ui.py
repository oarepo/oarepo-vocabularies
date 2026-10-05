# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Vocabulary type UI JSON serializer."""

from __future__ import annotations

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from oarepo_vocabularies.services.ui_schema import VocabularyUISchema


class VocabularyUIJSONSerializer(MarshmallowSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=VocabularyUISchema,
            list_schema_cls=BaseListSchema,
        )

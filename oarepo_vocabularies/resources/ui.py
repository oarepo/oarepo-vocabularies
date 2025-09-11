#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabulary type UI JSON serializer."""

from __future__ import annotations

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from oarepo_vocabularies.services.type_ui_schema import VocabularyTypeUISchema


class VocabularyTypeUIJSONSerializer(MarshmallowSerializer):
    """Vocabulary type UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=VocabularyTypeUISchema,
            list_schema_cls=BaseListSchema,
        )

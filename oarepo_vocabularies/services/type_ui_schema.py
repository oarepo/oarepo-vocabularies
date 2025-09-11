#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI schema for vocabulary types."""

from __future__ import annotations

from typing import Any

from flask_resources import BaseObjectSchema
from marshmallow import post_dump

from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField


class VocabularyTypeUISchema(BaseObjectSchema):
    """UI schema for vocabulary types."""

    name = VocabularyI18nStrUIField()

    description = VocabularyI18nStrUIField()

    @post_dump(pass_original=True)
    def keep_unknowns(self, output: dict, orig: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Keep unknown fields in the output."""
        for key in orig:  # noqa: PLC0206
            if key not in output:
                output[key] = orig[key]
        return output

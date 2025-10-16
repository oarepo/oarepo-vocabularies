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
from invenio_vocabularies.resources.serializer import L10NString
from marshmallow import post_dump


class VocabularyTypeUISchema(BaseObjectSchema):
    """UI schema for vocabulary types."""

    title = L10NString(data_key="title_l10n")
    description = L10NString(data_key="description_l10n")

    @post_dump(pass_original=True)
    def keep_unknowns(self, output: dict, orig: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Keep unknown fields in the output."""
        for key in orig:  # noqa: PLC0206
            # if output contains transformed version of the key, skip it
            if any(out_key.startswith(f"{key}_") for out_key in output):
                continue

            output[key] = orig[key]
        return output

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Schemas for vocabularies."""

from __future__ import annotations

from functools import partial
from typing import Any

import marshmallow as ma
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import fields as ma_fields
from marshmallow import post_load
from marshmallow_utils.fields import IdentifierSet, IdentifierValueSet, NestedAttribute


class HierarchySchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String(attribute="parent_id")
    level = ma_fields.Integer()
    titles = ma_fields.List(i18n_strings)
    ancestors = ma_fields.List(ma_fields.String(), attribute="ancestors_ids")
    ancestors_or_self = ma_fields.List(ma_fields.String(), attribute="ancestors_or_self_ids")
    leaf = ma_fields.Boolean()


class IdentifierSchema(ma.Schema):
    """A non-scheme validated identifier."""

    identifier = ma.fields.String(required=True)
    scheme = ma.fields.String(required=True)


class VocabularySchema(InvenioVocabularySchema):
    """Schema for vocabularies."""

    hierarchy = NestedAttribute(HierarchySchema, dump_only=True, attribute="hierarchy")

    custom_fields = NestedAttribute(partial(CustomFieldsSchema, fields_var="VOCABULARIES_CF"))

    identifiers = IdentifierSet(ma.fields.Nested(IdentifierSchema))

    crosswalks = IdentifierValueSet(ma.fields.Nested(IdentifierSchema))

    @post_load(pass_original=True)
    def extract_parent_id(self, data: dict, original_data: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Extract and set parent id from hierarchy."""
        hierarchy = original_data.get("hierarchy", {})
        parent = hierarchy.get("parent")
        if parent:
            data["parent"] = {"id": parent}
        else:
            data.pop("parent", None)
        return data

    @ma.post_dump
    def replace_none_custom_fields(self, data: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Replace None custom_fields with empty dict."""
        if data.get("custom_fields") is None:
            data["custom_fields"] = {}
        return data

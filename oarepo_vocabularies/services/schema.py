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
from marshmallow_utils.fields import NestedAttribute


class HierarchySchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String(attribute="parent_id")
    level = ma_fields.Integer()
    titles = ma_fields.List(i18n_strings)
    ancestors = ma_fields.List(ma_fields.String(), attribute="ancestors_ids")
    ancestors_or_self = ma_fields.List(ma_fields.String(), attribute="ancestors_or_self_ids")
    leaf = ma_fields.Boolean()


class SKOSMappingSchema(ma.Schema):
    """SKOS mapping schema."""

    identifier = ma_fields.String(required=True)
    scheme = ma_fields.String(required=True)
    relation = ma_fields.String(
        required=True,
        validate=[ma.validate.OneOf(["exactMatch", "broadMatch", "narrowMatch", "closeMatch", "relatedMatch"])],
    )
    """Relation type for the mapping.

    Meaning for the relation type:
        - exactMatch: this vocabulary matches exactly with the target vocabulary.
                      It can be used for both import and export.
        - broadMatch: the identifier is broader than our vocabulary.
                      It can be used for export and not for import.
        - narrowMatch: the identifier is narrower than our vocabulary.
                      It can be used for import and not for export.
        - closeMatch: the identifier is close to our vocabulary.
                      It can not be used for import or export.
        - relatedMatch: the identifier is related to our vocabulary.
                      It can not be used for import or export.
    """


class VocabularySchema(InvenioVocabularySchema):
    """Schema for vocabularies."""

    hierarchy = NestedAttribute(HierarchySchema, dump_only=True, attribute="hierarchy")

    custom_fields = NestedAttribute(partial(CustomFieldsSchema, fields_var="VOCABULARIES_CF"))

    mappings = ma.fields.List(ma.fields.Nested(SKOSMappingSchema))

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

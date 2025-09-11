#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Configuration for vocabulary resource."""

from __future__ import annotations

from functools import cached_property
from typing import Any, ClassVar

from flask_resources import BaseListSchema, MarshmallowSerializer, ResponseHandler
from flask_resources.serializers import JSONSerializer
from importlib_metadata import entry_points
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_vocabularies.resources.config import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.config import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import fields
from marshmallow_oneofschema import OneOfSchema

from oarepo_vocabularies.services.ui_schema import (
    VocabularySpecializedUISchema,
    VocabularyUISchema,
)


class VocabularySearchRequestArgsSchema(InvenioVocabularySearchRequestArgsSchema):
    """Request args schema for vocabulary search."""

    parent = fields.List(fields.String(), data_key="h-parent", attribute="h-parent")
    ancestor = fields.List(fields.String(), data_key="h-ancestor", attribute="h-ancestor")
    level = fields.List(fields.Integer(), data_key="h-level", attribute="h-level")

    def _deserialize(self, *args: Any, **kwargs: Any) -> Any:
        return super()._deserialize(*args, **kwargs)


class VocabularySchemaSelector(OneOfSchema):
    """Select vocabulary schema based on the type."""

    @cached_property
    def type_schemas(self) -> dict:
        """Get vocabulary type schemas from entry points."""
        ui_schemas = {
            "vocabulary": VocabularyUISchema,
            "*": VocabularySpecializedUISchema,
        }
        for ep in entry_points().select(group="oarepo_vocabularies.ui_schemas"):
            ui_schemas.update(ep.load())

        return ui_schemas

    def get_obj_type(self, obj: dict) -> str:
        """Determine the type of the object for schema selection."""
        from flask_resources import resource_requestctx

        if "type" in obj:
            return "vocabulary"
        vocabulary_type = resource_requestctx.view_args.get("type")
        if vocabulary_type in self.type_schemas:
            return vocabulary_type
        return "*"

    def dump(self, obj: Any, *, many: bool | None = None, **kwargs: Any) -> dict:
        """Dump the object using the selected schema."""
        ret = super().dump(obj, many=many, **kwargs)
        if ret.get("type") == "*":
            ret.pop("type")
        return ret


class VocabulariesUIResponseHandler(ResponseHandler):
    """UI JSON response handler."""

    serializer = MarshmallowSerializer(
        format_serializer_cls=JSONSerializer,
        object_schema_cls=VocabularySchemaSelector,
        list_schema_cls=BaseListSchema,
    )

    def __init__(self, headers: dict[str, str] | None = None):
        """Initialise Response Handler."""
        super().__init__(self.serializer, headers)


class VocabulariesResourceConfig(InvenioVocabulariesResourceConfig):
    """Vocabulary resource config."""

    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers: ClassVar[dict[str, ResponseHandler]] = {
        **InvenioVocabulariesResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": VocabulariesUIResponseHandler(
            headers=etag_headers,
        ),
    }

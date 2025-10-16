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

from typing import TYPE_CHECKING, ClassVar

from flask_resources import ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_vocabularies.resources.config import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.config import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import Schema, fields

from oarepo_vocabularies.resources.records.ui import VocabularyUIJSONSerializer

if TYPE_CHECKING:
    from collections.abc import Mapping


class VocabularySearchRequestArgsSchema(InvenioVocabularySearchRequestArgsSchema):
    """Request args schema for vocabulary search."""

    parent = fields.List(fields.String(), data_key="h-parent", attribute="h-parent")
    ancestor = fields.List(fields.String(), data_key="h-ancestor", attribute="h-ancestor")
    level = fields.List(fields.Integer(), data_key="h-level", attribute="h-level")


class VocabularyTypeRequestArgsSchema(Schema):
    """Request args schema for vocabulary search."""

    type_ = fields.String(data_key="type", attribute="type_")


class VocabulariesResourceConfig(InvenioVocabulariesResourceConfig):
    """Vocabulary resource config."""

    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers: ClassVar[Mapping[str, ResponseHandler]] = {  # type: ignore[override]
        **InvenioVocabulariesResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(VocabularyUIJSONSerializer(), headers=etag_headers),
    }

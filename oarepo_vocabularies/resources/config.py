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

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from flask_resources import ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_vocabularies.resources.config import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.config import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import ValidationError, fields
from marshmallow.validate import Validator

from oarepo_vocabularies.resources.records.ui import VocabularyUIJSONSerializer

if TYPE_CHECKING:
    from collections.abc import Mapping


class ISO8601Validator(Validator):
    """Validate that a string is an ISO8601-formatted date or datetime.

    Mirrors marshmallow_utils.fields.edtfdatestring.EDTFValidator: it validates the string
    in place rather than converting it to a date/datetime object, so callers that only need
    to pass the value through (e.g. into an OpenSearch range query) keep it as a plain string.
    """

    default_message = "Please provide a valid ISO8601-formatted date or datetime."

    def __init__(self, error: str | None = None) -> None:
        """Create an instance of the validator."""
        self._error = error or self.default_message

    def __call__(self, value: str) -> str:
        """Validate."""
        try:
            datetime.fromisoformat(value)
        except ValueError as e:
            raise ValidationError(self._error) from e
        return value


class VocabularySearchRequestArgsSchema(InvenioVocabularySearchRequestArgsSchema):
    """Request args schema for vocabulary search."""

    parent = fields.List(fields.String(), data_key="h-parent", attribute="h-parent")
    ancestor = fields.List(fields.String(), data_key="h-ancestor", attribute="h-ancestor")
    level = fields.List(fields.Integer(), data_key="h-level", attribute="h-level")
    skos = fields.List(fields.String(), data_key="skos", attribute="skos")
    newer = fields.String(data_key="newer", attribute="newer", validate=ISO8601Validator())


class VocabulariesResourceConfig(InvenioVocabulariesResourceConfig):
    """Vocabulary resource config."""

    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers: ClassVar[Mapping[str, ResponseHandler]] = {  # type: ignore[override]
        **InvenioVocabulariesResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(VocabularyUIJSONSerializer(), headers=etag_headers),
    }

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Schemas for vocabularies UI."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import marshmallow as ma
from flask import current_app
from invenio_i18n import get_locale
from invenio_rdm_records.resources.serializers.ui.schema import FormatDate

# TODO: udelat znova from oarepo_runtime.services.schema.cf import CustomFieldsSchemaUI
from invenio_records_resources.services.custom_fields.schema import (
    CustomFieldsSchemaUI as InvenioCustomFieldsSchemaUI,
)
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow import fields as ma_fields
from marshmallow import post_dump

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


class LocalizedDateTime(ma.fields.Field):
    """A Marshmallow field that provides localized datetime formatting."""

    def __init__(self, attribute: str, **kwargs: Any) -> None:
        """Initialize the LocalizedDateTime field."""
        super().__init__(**kwargs)
        self.attribute = attribute

        self.formatters = {
            "short": FormatDate(attribute=attribute, format="short"),
            "medium": FormatDate(attribute=attribute, format="medium"),
            "long": FormatDate(attribute=attribute, format="long"),
            "full": FormatDate(attribute=attribute, format="full"),
        }

    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> dict:
        return {
            f"{self.attribute}_l10n_{fmt}": formatter._serialize(value, attr, obj, **kwargs)  # noqa: SLF001
            for fmt, formatter in self.formatters.items()
        }


class CustomFieldsSchemaUI(InvenioCustomFieldsSchemaUI):
    """Custom fields schema for UI."""

    def _serialize(self, obj: Any, **kwargs: Any) -> Any:
        self._schema.context.update(self.context)
        return super()._serialize(obj, **kwargs)

    def _deserialize(self, data: Mapping[str, Any] | Iterable[Mapping[str, Any]], **kwargs: Any) -> Any:
        self._schema.context.update(self.context)
        return super()._deserialize(data, **kwargs)


class VocabularyI18nStrUIField(ma_fields.Field):
    """A Marshmallow field that provides localized string from i18n dict."""

    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> Any:  # noqa: ARG002
        if not value:
            return None
        locale = self.get_locale()
        if locale:
            language = locale.language
            if language in value:
                return value[language]
        locale = current_app.config["BABEL_DEFAULT_LOCALE"]
        if locale in value:
            return value[locale]
        return next(iter(value.values()))

    def get_locale(self) -> Any:
        """Get locale from context or current locale."""
        if isinstance(self.context, dict) and "locale" in self.context:
            return self.context["locale"]
        locale = get_locale()
        if self.context is not None:
            self.context["locale"] = locale
        return locale


class HierarchyUISchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String()
    level = ma_fields.Integer()
    titles = ma_fields.List(VocabularyI18nStrUIField())
    ancestors = ma_fields.List(ma_fields.String())
    ancestors_or_self = ma_fields.List(ma_fields.String())
    leaf = ma.fields.Boolean()


class VocabularyUISchema(InvenioVocabularySchema):
    """Vocabulary UI schema."""

    custom_fields = ma_fields.Nested(partial(CustomFieldsSchemaUI, fields_var="VOCABULARIES_CF"))
    hierarchy = ma_fields.Nested(HierarchyUISchema)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the vocabulary UI schema."""
        super().__init__(*args, **kwargs)

    created = LocalizedDateTime(attribute="created", dump_only=True)
    updated = LocalizedDateTime(attribute="updated", dump_only=True)

    links = ma.fields.Raw(dump_only=True)
    title = VocabularyI18nStrUIField()
    type = ma.fields.Raw(dump_only=True)
    description = VocabularyI18nStrUIField()
    props = ma.fields.Dict(keys=ma.fields.String(), values=ma.fields.String())

    @post_dump(pass_original=True)
    def create_rdm_structure(self, data: dict, original: Any, **kwargs: Any) -> dict:  # noqa: ARG002
        """Create Invenio RDM structure with original data and UI data under 'ui' key."""
        # Get the context to check if we should create RDM structure
        context = self.context or {}
        object_key = context.get("object_key")

        if object_key == "ui":
            # Create the RDM format: {**original_record, ui: {ui_data}}
            return {**original, "ui": {**data}}

        return data

    @post_dump(pass_original=False)
    def flatten_localized_dates(self, data: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Flatten localized date fields into the UI dictionary."""
        # Only flatten if we're working on UI data (not the top-level RDM structure)
        context = self.context or {}
        object_key = context.get("object_key")

        if object_key == "ui" and "ui" in data:
            # If this is RDM structure, flatten dates in the UI section
            ui_data = data["ui"]
            for date_field in ["created", "updated"]:
                if date_field in ui_data:
                    date_info = ui_data.pop(date_field)
                    if isinstance(date_info, dict):
                        ui_data.update(date_info)

        return data

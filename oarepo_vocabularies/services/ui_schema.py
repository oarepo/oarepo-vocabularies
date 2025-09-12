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

import copy
from functools import partial
from typing import TYPE_CHECKING, Any

import marshmallow as ma
from flask import current_app
from invenio_i18n import get_locale

# TODO: udelat znova from oarepo_runtime.services.schema.cf import CustomFieldsSchemaUI
from invenio_records_resources.services.custom_fields.schema import (
    CustomFieldsSchemaUI as InvenioCustomFieldsSchemaUI,
)
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow import fields as ma_fields
from marshmallow_utils.fields import FormatDate

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


class LocalizedDateTime(ma.fields.Field):
    """A Marshmallow field that provides localized datetime formatting."""

    def __init__(self, attribute: str, **kwargs: Any) -> None:
        """Initialize the LocalizedDateTime field."""
        super().__init__(**kwargs)
        self.attribute = attribute

    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> dict:  # noqa: ARG002
        return {
            f"{self.attribute}_l10n_long": FormatDate(
                attribute=self.attribute,
                format="long",
            ),
            f"{self.attribute}_l10n_medium": FormatDate(
                attribute=self.attribute,
                format="medium",
            ),
            f"{self.attribute}_l10n_short": FormatDate(
                attribute=self.attribute,
                format="short",
            ),
            f"{self.attribute}_l10n_full": FormatDate(
                attribute=self.attribute,
                format="full",
            ),
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
    title = ma_fields.List(VocabularyI18nStrUIField())
    ancestors = ma_fields.List(ma_fields.String())
    ancestors_or_self = ma_fields.List(ma_fields.String())


class VocabularyUISchema(InvenioVocabularySchema):
    """Vocabulary UI schema."""

    hierarchy = ma_fields.Nested(partial(CustomFieldsSchemaUI, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF"))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the vocabulary UI schema."""
        super().__init__(*args, **kwargs)

    created = LocalizedDateTime("created", dump_only=True)
    updated = LocalizedDateTime("updated", dump_only=True)
    links = ma.fields.Raw(dump_only=True)
    title = VocabularyI18nStrUIField()
    type = ma.fields.Raw(dump_only=True)
    description = VocabularyI18nStrUIField()
    props = ma.fields.Dict(keys=ma.fields.String(), values=ma.fields.String())


class VocabularySpecializedUISchema(VocabularyUISchema):
    """Specialized vocabulary schema."""

    @ma.post_dump(pass_many=False, pass_original=True)
    def dump_extra_fields(self, data: dict, original_data: dict, **kwargs: Any) -> dict:  # noqa: ARG002
        """Dump extra fields from original data."""
        for k, v in original_data.items():
            if k not in data:
                data[k] = copy.deepcopy(v)
        return data

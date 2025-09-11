#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Custom fields for hierarchy in vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_records_resources.services.custom_fields import BooleanCF
from invenio_records_resources.services.custom_fields.base import BaseCF
from invenio_records_resources.services.custom_fields.number import IntegerCF
from invenio_records_resources.services.custom_fields.text import KeywordCF
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import fields as ma_fields

from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField

if TYPE_CHECKING:
    from invenio_records_resources.records.api import Record


class HierarchyCF:
    """Base class for hierarchy custom fields."""

    def update(self, record: Record, parent: Record | None) -> None:
        """Update the record with hierarchy information."""


class HierarchyLevelCF(HierarchyCF, IntegerCF):
    """Hierarchy level custom field."""

    def update(self, record: Record, parent: Record | None) -> None:
        """Update the record with hierarchy level information."""
        record.hierarchy["level"] = (parent["hierarchy"]["level"] + 1) if parent else 1


class HierarchyTitleCF(HierarchyCF, BaseCF):
    """Hierarchy title custom field."""

    def update(self, record: Record, parent: Record | None) -> None:
        """Update the record with hierarchy title information."""
        titles = [record["title"]] if record.get("title") else []
        if parent:
            titles.extend(parent["hierarchy"]["title"])
        record.hierarchy["title"] = titles

    @property
    def mapping(self) -> dict:
        """Return the Elasticsearch mapping for the field."""
        return {"type": "object", "dynamic": True}

    @property
    def field(self) -> ma_fields.List:
        """Return the Marshmallow field for the field."""
        return ma_fields.List(i18n_strings)

    @property
    def ui_field(self) -> ma_fields.List:
        """Return the Marshmallow UI field for the field."""
        return ma_fields.List(VocabularyI18nStrUIField())


class HierarchyAncestorsCF(HierarchyCF, KeywordCF):
    """Hierarchy ancestors custom field."""

    def update(self, record: Record, parent: Record | None) -> None:
        """Update the record with hierarchy ancestors information."""
        if parent:
            record.hierarchy["ancestors"] = [
                parent["id"],
                *parent["hierarchy"]["ancestors"],
            ]
        else:
            record.hierarchy["ancestors"] = []


class HierarchyAncestorsOrSelfCF(HierarchyCF, KeywordCF):
    """Hierarchy ancestors or self custom field."""

    def update(self, record: Record, parent: Record | None) -> None:
        """Update the record with hierarchy ancestors or self information."""
        if parent:
            record.hierarchy["ancestors_or_self"] = [
                record["id"],
                *parent["hierarchy"]["ancestors_or_self"],
            ]
        else:
            record.hierarchy["ancestors_or_self"] = [record["id"]]


class HierarchyLeafCF(HierarchyCF, BooleanCF):
    """Hierarchy leaf custom field."""

    def update(self, record: Record, parent: Record | None) -> None:  # noqa: ARG002
        """Update the record with hierarchy leaf information."""
        # initial value
        if "leaf" not in record.hierarchy:
            record.hierarchy["leaf"] = True

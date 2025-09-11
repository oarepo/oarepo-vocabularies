#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Hierarchy system field for vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_db import db
from invenio_records.systemfields import SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin
from oarepo_runtime.records.systemfields.selectors import PathSelector

from oarepo_vocabularies.records.models import VocabularyHierarchy

from .helpers import HierarchyObject

if TYPE_CHECKING:
    from invenio_records_resources.records.api import Record


class HierarchySystemField(MappingSystemFieldMixin, SystemField):
    """System field handling the VocabularyHierarchy hierarchy fields fixes on create/update/delete of a record."""

    def __get__(self, record: Record, owner: Any = None) -> Any:
        """Get the hierarchy field value or cached value."""
        if record is None:
            return self

        if not hasattr(record, "_hierarchy_cache"):
            record._hierarchy_cache = HierarchyObject(record)  # noqa: SLF001

        return record._hierarchy_cache  # noqa: SLF001

    @property
    def mapping(self) -> dict[str, Any]:
        """Get the mapping for the hierarchy field."""
        return {
            self.key: {
                "type": "object",
                "enabled": True,
                "properties": {
                    "parent": {
                        "type": "keyword",
                    },
                    "level": {"type": "integer"},
                    "titles": {"type": "object", "enabled": False},
                    "ancestors": {"type": "keyword"},
                    "ancestors_or_self": {"type": "keyword"},
                    "leaf": {"type": "boolean"},
                },
            }
        }

    def pre_commit(self, record: Record) -> None:
        """Fix the parent leaf status and update children hierarchy on create/update."""
        hierarchy_obj = self.__get__(record)
        hierarchy_obj._hierarchy_data.fix_hierarchy_on_self()  # noqa: SLF001

        # Store information about whether we need to fix descendants
        # We have new parent or we had no parent
        parent_changed = record.parent.uuid != record.parent.previous_uuid or (
            record.parent.uuid and not record.parent.previous_uuid
        )

        hierarchy_obj._hierarchy_data.update_parent_leaf_status(record.parent)  # noqa: SLF001

        if parent_changed:
            hierarchy_obj._hierarchy_data.fix_hierarchy_down()  # noqa: SLF001

    def pre_delete(self, record: Record, force: bool = False) -> None:  # noqa: ARG002
        """Fix the parent leaf status and update children hierarchy on delete."""
        hierarchy_obj = self.__get__(record)

        hierarchy_obj._hierarchy_data.update_parent_leaf_status(record.parent)  # noqa: SLF001

        # update children hierarchy
        hierarchy_obj._hierarchy_data.fix_hierarchy_down_on_delete()  # noqa: SLF001

        # delete after children are updated
        hierarchy_entry = VocabularyHierarchy.query.get(record.id)
        if hierarchy_entry:
            db.session.delete(hierarchy_entry)

    def pre_dump(self, record: Record, data: dict[str, Any], dumper: Any = None) -> None:  # noqa: ARG002
        """Add the hierarchy data to the record before dumping."""
        hierarchy_obj = self.__get__(record)
        data[self.key] = hierarchy_obj.to_dict()


class HierarchyPartSelector(PathSelector):
    """Selector selecting part of hierarchy."""

    level = 0

    def __init__(self, *paths: tuple[str], level: int | None = None) -> None:
        """Initialize the selector."""
        super().__init__(*paths)
        if level is not None:
            self.level = level
        if not self.paths:
            raise ValueError("At least one path must be set")

    def select(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Select the correct part of hierarchy."""
        parts = super().select(data)

        elements = []
        for dg in parts:
            ids = dg["hierarchy"]["ancestors_or_self"]
            titles = dg["hierarchy"]["title"]
            if len(ids) > self.level:
                elements.append({"id": ids[-1 - self.level], "title": titles[-1 - self.level]})
        return elements

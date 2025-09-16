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
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin
from oarepo_runtime.records.systemfields.selectors import PathSelector

from oarepo_vocabularies.records.models import VocabularyHierarchy

if TYPE_CHECKING:
    from invenio_records.api import RecordBase
    from invenio_records.dumpers import Dumper
    from invenio_records_resources.records.api import Record

    from oarepo_vocabularies.records.api import Vocabulary as OarepoVocabularyRecord


class HierarchyObject:
    """Object representing the hierarchy data of a vocabulary record.

    References the VocabularyHierarchy table row and provides methods to interact with it.
    """

    def __init__(self, record: OarepoVocabularyRecord):
        """Initialize the HierarchyObject."""
        self._record = record
        self._hierarchy_data: VocabularyHierarchy = self._record.model.hierarchy_metadata  # type: ignore[union-attr]

        if self._hierarchy_data is None:
            self._hierarchy_data = VocabularyHierarchy()
            self._hierarchy_data.id = self._record.id
            self._hierarchy_data.parent_id = (
                getattr(self._record.parent, "uuid", None) if hasattr(self._record, "parent") else None
            )
            self._hierarchy_data.pid = self._record["id"]
            self._hierarchy_data.titles = [self._record.get("title")]

    @property
    def data(self) -> VocabularyHierarchy:
        """Get the hierarchy data."""
        return self._hierarchy_data

    def to_dict(self) -> dict[str, Any]:
        """Convert the hierarchy data to a dictionary."""
        return {
            "level": self._hierarchy_data.level,
            "titles": self._hierarchy_data.titles,
            "ancestors": self._hierarchy_data.ancestors,
            "ancestors_or_self": self._hierarchy_data.ancestors_or_self,
            "leaf": self._hierarchy_data.leaf,
            "parent": self._hierarchy_data.ancestors[0] if self._hierarchy_data.ancestors else None,
        }

    def query_subterms(self) -> Any:
        """Get direct subterms of this record."""
        subterm_ids = self._hierarchy_data.get_direct_subterms_ids(self._record.id)
        return Vocabulary.get_records(subterm_ids)

    def query_descendants(self) -> Any:
        """Get all descendants (children, grandchildren, etc.) of this record."""
        descendants_ids = self._hierarchy_data.get_subterms_ids(self._record.id)
        return Vocabulary.get_records(descendants_ids)

    @property
    def level(self) -> int:
        """Get the level of the record in the hierarchy."""
        return self._hierarchy_data.level

    @property
    def leaf(self) -> bool:
        """Check if the record is a leaf in the hierarchy."""
        return self._hierarchy_data.leaf

    @property
    def titles(self) -> list[dict[str, str]]:
        """Get the titles of the hierarchy."""
        return self._hierarchy_data.titles

    @property
    def ancestors_ids(self) -> list[str]:
        """Get the PIDs of the ancestors in the hierarchy."""
        return self._hierarchy_data.ancestors

    @property
    def ancestors_or_self_ids(self) -> list[str]:
        """Get the PIDs of the ancestors or self in the hierarchy."""
        return self._hierarchy_data.ancestors_or_self

    @property
    def parent_id(self) -> str | None:
        """Get the PID of the parent in the hierarchy."""
        return self._hierarchy_data.ancestors[0] if self._hierarchy_data.ancestors else None


class HierarchySystemField(MappingSystemFieldMixin, SystemField):
    """System field handling the VocabularyHierarchy hierarchy fields fixes on create/update/delete of a record."""

    def __get__(self, record: Record, owner: Any = None) -> Any:
        """Get the hierarchy field value or cached value."""
        if record is None:
            return self

        if not hasattr(record, "_hierarchy_cache"):
            record._hierarchy_cache = HierarchyObject(record)  # noqa: SLF001 # type: ignore[attr-defined]

        return record._hierarchy_cache  # noqa: SLF001 # type: ignore[attr-defined]

    @property
    def mapping(self) -> dict[str, Any]:
        """Get the mapping for the hierarchy field."""
        key = self.key
        if key is None:
            raise ValueError("Field key cannot be None")

        return {
            key: {
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
        hierarchy_obj.data.fix_hierarchy_on_self()

        # Store information about whether we need to fix descendants
        # We have new parent or we had no parent
        parent_changed = record.parent.uuid != record.parent.previous_uuid or (  # type: ignore[attr-defined]
            record.parent.uuid and not record.parent.previous_uuid  # type: ignore[attr-defined]
        )

        hierarchy_obj.data.update_parent_leaf_status(record.parent)  # type: ignore[attr-defined]

        if parent_changed:
            hierarchy_obj.data.fix_hierarchy_down()

    def pre_delete(self, record: Record, force: bool = False) -> None:  # noqa: ARG002
        """Fix the parent leaf status and update children hierarchy on delete."""
        hierarchy_obj = self.__get__(record)

        hierarchy_obj.data.update_parent_leaf_status(record.parent)  # type: ignore[attr-defined]

        # update children hierarchy
        hierarchy_obj.data.fix_hierarchy_down_on_delete()

        # delete after children are updated
        hierarchy_entry = VocabularyHierarchy.query.get(record.id)
        if hierarchy_entry:
            db.session.delete(hierarchy_entry)

    def pre_dump(self, record: RecordBase, data: dict, dumper: Dumper | None = None) -> None:  # noqa: ARG002
        """Add the hierarchy data to the record before dumping."""
        hierarchy_obj = self.__get__(record)  # type: ignore[arg-type]
        data[self.key] = hierarchy_obj.to_dict()


class HierarchyPartSelector(PathSelector):
    """Selector selecting part of hierarchy."""

    level = 0

    def __init__(self, *paths: str, level: int | None = None) -> None:
        """Initialize the selector."""
        super().__init__(*paths)
        if level is not None:
            self.level = level
        if not self.paths:
            raise ValueError("At least one path must be set")

    def select(self, record: dict) -> list[Any]:
        """Select the correct part of hierarchy."""
        parts = super().select(record)

        elements = []
        for dg in parts:
            ids = dg["hierarchy"]["ancestors_or_self"]
            titles = dg["hierarchy"]["title"]
            if len(ids) > self.level:
                elements.append({"id": ids[-1 - self.level], "title": titles[-1 - self.level]})
        return elements

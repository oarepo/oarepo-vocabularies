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
            # Opensearch result creates transient self._record.model so that hiearchy_metadata is not loaded from the DB
            existing = db.session.query(VocabularyHierarchy).filter_by(id=self._record.id).one_or_none()
            if existing is not None:
                self._hierarchy_data = existing
            else:
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

    def __get__(self, record: Record, owner: Any = None) -> Any:  # type: ignore[override]
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

    def pre_commit(self, record: OarepoVocabularyRecord) -> None:
        """Fix the parent leaf status and update children hierarchy on create/update."""
        hierarchy_obj = self.__get__(record)
        current_parent_id = record.parent.id

        # We have a current parent set, check if it changed
        if current_parent_id:
            current_parent_record = Vocabulary.pid.with_type_ctx(record["type"]["id"]).resolve(current_parent_id)  # type: ignore[attr-defined]

            if hierarchy_obj.data.parent_id != current_parent_record.id:
                # update the parent_id and parent_hierarchy_metadata, relationship will not change automatically
                # with this current record will fix itself with fix_hierarchy_on_self correctly
                hierarchy_obj.data.parent_id = current_parent_record.id
                hierarchy_obj.data.parent_hierarchy_metadata = VocabularyHierarchy.query.get(current_parent_record.id)
                db.session.flush()

        parent_changed = record.parent.id != record.parent.previous_id
        # parent was removed, update the parent_id and parent_hierarchy_metadata in DB
        # so current record fixes with fix_hierarchy_on_self correctly
        if parent_changed and not record.parent.id and record.parent.previous_id:
            hierarchy_obj.data.parent_id = None
            hierarchy_obj.data.parent_hierarchy_metadata = None
            db.session.flush()

        hierarchy_obj.data.fix_hierarchy_on_self()

        # We have new parent or we had no parent
        # Update the parent leaf status
        if hierarchy_obj.data.parent_hierarchy_metadata is not None:
            hierarchy_obj.data.parent_hierarchy_metadata.update_leaf_status(force_child_exists=True)

        if parent_changed:
            # potentially fix our children (if we have any)
            hierarchy_obj.data.fix_hierarchy_down()

            # potentially fix the previous parent leaf status
            if record.parent.previous_id is not None:
                previous_parent_record = Vocabulary.pid.with_type_ctx(record["type"]["id"]).resolve(  # type: ignore[attr-defined]
                    record.parent.previous_id
                )
                previous_parent_hierarchy = VocabularyHierarchy.query.get(previous_parent_record.id)
                if previous_parent_hierarchy is not None:
                    previous_parent_hierarchy.update_leaf_status()

    def pre_delete(self, record: Record, force: bool = False) -> None:  # noqa: ARG002
        """Fix the parent leaf status and update children hierarchy on delete."""
        # update current record to have no parent
        hierarchy_entry = VocabularyHierarchy.query.get(record.id)
        if hierarchy_entry is None:
            return  # raise error? just ignore?

        # save for later use
        parent_hierarchy_metadata = hierarchy_entry.parent_hierarchy_metadata

        # delete the current record DB entry
        db.session.delete(hierarchy_entry)

        if parent_hierarchy_metadata is not None:
            parent_hierarchy_metadata.update_leaf_status()

    def pre_dump(self, record: RecordBase, data: dict, dumper: Dumper | None = None) -> None:  # noqa: ARG002
        """Add the hierarchy data to the record before dumping."""
        hierarchy_obj = self.__get__(record)  # type: ignore[arg-type]
        data[self.key] = hierarchy_obj.to_dict()

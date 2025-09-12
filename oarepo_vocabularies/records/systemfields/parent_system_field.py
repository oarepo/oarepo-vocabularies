#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Parent system field for vocabulary records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_db import db
from invenio_records.systemfields import DictField, SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.records.models import VocabularyHierarchy

from .helpers import ParentObject

if TYPE_CHECKING:
    from invenio_records_resources.records.api import Record

    from oarepo_vocabularies.records.api import Vocabulary as OarepoVocabularyRecord


class ParentSystemField(MappingSystemFieldMixin, SystemField):
    """System field handling the VocabularyHierarchy parent column updates on create/update/delete of a record."""

    def __init__(self, key: str | None = None, clear_none: bool = False, create_if_missing: bool = True):
        """Initialize the ParentSystemField."""
        self.clear_none = clear_none
        self.create_if_missing = create_if_missing
        super().__init__(key=key)

        self._dict_field = DictField(key=key, clear_none=clear_none, create_if_missing=create_if_missing)

    @property
    def mapping(self) -> dict[str, Any]:
        """Get the mapping for the parent field."""
        key = self.key
        if key is None:
            raise ValueError("Field key cannot be None")

        return {
            key: {
                "type": "object",
                "enabled": True,
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "object", "enabled": False},
                },
            }
        }

    def __set_name__(self, owner: Any, name: str) -> None:
        """Set the name of the field."""
        super().__set_name__(owner, name)
        self._dict_field.__set_name__(owner, name)

    def __get__(self, record: Record, owner: Any = None) -> Any:
        """Get the parent field value or cached value."""
        if record is None:
            return self

        if not hasattr(record, "_parent_cache"):
            record._parent_cache = ParentObject(self._dict_field, record)  # noqa: SLF001 # type: ignore[attr-defined]

        return record._parent_cache  # noqa: SLF001 # type: ignore[attr-defined]

    def __set__(self, record: Record, value: dict | None):  # type: ignore[override]
        """Set the parent field value."""
        self.__get__(record).set(value)

    def pre_commit(self, record: OarepoVocabularyRecord) -> None:
        """Handle updates by updating/inserting row in VocabularyHierarchy table.

        When record is updated/created, we add/change the parent to a actual one in VocabularyHierarchy table.
        """
        cache = self.__get__(record)

        parent = record.relations.parent()
        if parent:
            parent_uuid = parent.id
            self_uuid = record.id

            hierarchy_entry = VocabularyHierarchy.query.get(self_uuid)

            if hierarchy_entry:
                # Update existing row
                if hierarchy_entry.parent_id != parent_uuid:
                    hierarchy_entry.parent_id = parent_uuid

                # check if title is the same
                if record.get("title") != hierarchy_entry.titles[0]:
                    hierarchy_entry.titles[0] = record.get("title")
            else:
                # Insert new row
                hierarchy_entry = VocabularyHierarchy()
                hierarchy_entry.id = self_uuid
                hierarchy_entry.parent_id = parent_uuid
                hierarchy_entry.pid = record.get("id")
                hierarchy_entry.titles = [record.get("title")]

                db.session.add(hierarchy_entry)

            # Use flush so it stays inside the same transaction
            db.session.flush()
        elif parent is None and cache.previous_uuid and not cache.uuid:
            # parent was removed, we need to update row in DB
            row = (
                db.session.query(VocabularyHierarchy)
                .filter(
                    VocabularyHierarchy.id == record.id,
                    VocabularyHierarchy.parent_id == cache.previous_uuid,
                )
                .one()
            )  # there is always will be one row, but this will catch any mistakes

            # remove also from db
            if row:
                row.parent_id = None
                db.session.add(row)
                db.session.flush()

    def pre_delete(self, record: Record, force: bool = False) -> None:  # noqa: ARG002
        """Handle deletion by setting correct parent to children in VocabularyHierarchy table."""
        cache = self.__get__(record)

        cache._previous_parent_uuid = cache.uuid  # noqa: SLF001
        cache._parent_uuid = None  # noqa: SLF001
        cache._parent_id = None  # noqa: SLF001
        self_uuid = record.id

        # If record has any children, set their parent to parent of the deleted record
        direct_children = VocabularyHierarchy.get_direct_subterms_ids(self_uuid)

        for child_id in direct_children:
            child_entry = VocabularyHierarchy.query.get(child_id)
            if child_entry:
                child_entry.parent_id = cache.previous_uuid
                db.session.add(child_entry)

        db.session.flush()

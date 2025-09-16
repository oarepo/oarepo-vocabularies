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
from invenio_vocabularies.records.api import Vocabulary
from marshmallow import ValidationError
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.records.models import VocabularyHierarchy

if TYPE_CHECKING:
    from uuid import UUID

    from invenio_records_resources.records.api import Record

    from oarepo_vocabularies.records.api import Vocabulary as OarepoVocabularyRecord


class ParentObject:
    """Object representing the parent data of a vocabulary record.

    Caches the current and previous parent UUIDs to detect changes and need for updates of Hierarchy.
    """

    def __init__(self, dict_field: DictField, record: OarepoVocabularyRecord):
        """Initialize the ParentObject."""
        self._dict_field = dict_field
        self._record = record
        self._previous_parent_uuid = None
        self._parent_uuid = None
        self._parent_id = None
        self._cached = False

    @property
    def uuid(self) -> UUID | None:
        """Get the current parent UUID."""
        if not self._cached:
            self._get_from_record()

        return self._parent_uuid

    @property
    def previous_uuid(self) -> UUID | None:
        """Get the previous parent UUID."""
        if not self._cached:
            self._get_from_record()
        return self._previous_parent_uuid

    def _get_from_record(self) -> None:
        """Get the parent UUIDs from the record relations."""
        parent = self._record.relations.parent()

        if parent:
            self._parent_uuid = parent.id
            self._previous_parent_uuid = (
                db.session.query(VocabularyHierarchy.parent_id)
                .filter(VocabularyHierarchy.id == self._record.id)
                .scalar()
            )
            self._parent_id = parent["id"]

            self._cached = True

    def set(self, value: Any) -> None:
        """Set the parent value."""
        if not self._cached:
            self._get_from_record()

        self._dict_field.__set__(self._record, value)
        parent_id = value.get("id")

        # no parent
        if not parent_id:
            self._previous_parent_uuid = self._parent_uuid
            self._parent_id = None
            self._parent_uuid = None
            return

        # changed parent
        if parent_id != self._parent_id:
            self._parent_id = parent_id
            self._previous_parent_uuid = self._parent_uuid  # current will be previous
            self._parent_uuid = Vocabulary.pid.with_type_ctx(self._record["type"]["id"]).resolve(parent_id).id  # type: ignore[attr-defined]
            self._cached = True


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

        # we have a parent, either new or changed
        if parent:
            parent_uuid = parent.id
            self_uuid = record.id

            hierarchy_entry = VocabularyHierarchy.query.get(self_uuid)
            # If hierarchy entry exists, update it
            if hierarchy_entry:
                # check if parent is the same
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
        # we had a parent, but now it is removed, because we moved to other "tree"
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

        # update cache values, because there are used later in updating hierarchy leaf status
        cache._previous_parent_uuid = cache.uuid  # noqa: SLF001
        cache._parent_uuid = None  # noqa: SLF001
        cache._parent_id = None  # noqa: SLF001
        self_uuid = record.id

        # Can only delete if has no children
        direct_children = VocabularyHierarchy.get_direct_subterms_ids(self_uuid)
        if len(direct_children) > 0:
            # TODO: Change to marshmallow validation error if has children
            raise ValidationError(
                {
                    "parent": f"Cannot delete a vocabulary term with ID {self_uuid} "
                    "that has children. Reassign or delete children first."
                }
            )

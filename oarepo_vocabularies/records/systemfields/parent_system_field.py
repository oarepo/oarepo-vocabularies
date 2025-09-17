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

from typing import TYPE_CHECKING, Any, cast

from invenio_records.systemfields import DictField, SystemField
from marshmallow import ValidationError
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.records.models import VocabularyHierarchy

if TYPE_CHECKING:
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
        self._previous_parent_id: str | None = None
        self._parent_id: str | None = None

    @property
    def id(self) -> str | None:
        """Get the current parent ID."""
        val = cast("dict[str, str] | None", self._dict_field.__get__(self._record))
        return val.get("id") if val else None

    @property
    def previous_id(self) -> str | None:
        """Get the previous parent ID."""
        return self._previous_parent_id

    def set(self, value: str | None) -> None:
        """Set the parent value."""
        if self._previous_parent_id is not None:
            raise ValueError("Parent value has already been set once.")
        self._previous_parent_id = self.id
        self._dict_field.__set__(self._record, {"id": value} if value is not None else None)


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

    def __set__(self, record: Record, value: str | None):  # type: ignore[override]
        """Set the parent field value."""
        self.__get__(record).set(value if value is not None else None)

    def pre_delete(self, record: Record, force: bool = False) -> None:  # noqa: ARG002
        """Handle deletion by setting correct parent to children in VocabularyHierarchy table."""
        self_uuid = record.id

        # Can only delete if has no children
        direct_children = VocabularyHierarchy.get_direct_subterms_ids(self_uuid)
        if len(direct_children) > 0:
            raise ValidationError(
                {
                    "parent": f"Cannot delete a vocabulary term with ID {record['id']} "
                    "that has children. Reassign or delete children first."
                }
            )

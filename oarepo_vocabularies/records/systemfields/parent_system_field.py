# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Parent system field for vocabulary records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from invenio_records.systemfields import SystemField
from marshmallow import ValidationError
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.records.models import VocabularyHierarchy

if TYPE_CHECKING:
    from invenio_records.api import Record as RecordBase
    from invenio_records_resources.records.api import Record

    from oarepo_vocabularies.records.api import Vocabulary as OarepoVocabularyRecord


class ParentObject:
    """Object representing the parent data of a vocabulary record.

    Caches the current and previous parent UUIDs to detect changes and need for updates of Hierarchy.
    """

    def __init__(self, key: str, record: OarepoVocabularyRecord):
        """Initialize the ParentObject."""
        if "." in key:
            raise ValueError("ParentObject only supports top-level keys.")
        self._key = key
        self._record = record
        self._previous_parent_id: str | None = None
        self._parent_id: str | None = None

    @property
    def id(self) -> str | None:
        """Get the current parent ID."""
        val: dict[str, str] = self._record.get(self._key, {})
        return val.get("id")

    @property
    def previous_id(self) -> str | None:
        """Get the previous parent ID."""
        return self._previous_parent_id

    def set(self, value: str | None) -> None:
        """Set the parent value."""
        if self._previous_parent_id is not None:
            raise ValueError("Parent value has already been set once.")
        self._previous_parent_id = self.id

        if not value:
            self._record.pop(self._key, None)
        else:
            self._record[self._key] = {"id": value}


class ParentSystemField(MappingSystemFieldMixin, SystemField):
    """System field handling the VocabularyHierarchy parent column updates on create/update/delete of a record."""

    def __init__(self, key: str | None = None):
        """Initialize the ParentSystemField."""
        super().__init__(key=key)

    @property
    @override
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

    @override
    def __get__(self, record: RecordBase | None, owner: Any = None) -> Any:
        """Get the parent field value or cached value."""
        if record is None:
            return self

        record = cast("OarepoVocabularyRecord", record)

        if not hasattr(record, "_parent_cache"):
            record._parent_cache = ParentObject(self.key, record)  # noqa:SLF001

        return record._parent_cache  # noqa:SLF001

    @override
    def __set__(self, record: RecordBase | None, value: str | None):
        """Set the parent field value."""
        self.__get__(record).set(value if value is not None else None)

    @override
    def pre_delete(self, record: Record, force: bool = False) -> None:
        """Handle deletion by setting correct parent to children in VocabularyHierarchy table."""
        self_uuid = record.id

        # Can only delete if has no children
        direct_children = VocabularyHierarchy.get_direct_subterms_ids(self_uuid)
        if len(direct_children) > 0:
            raise ValidationError(
                {
                    "parent": f"Cannot delete a vocabulary term with ID {record.get('id')} "
                    "that has children. Reassign or delete children first."
                }
            )

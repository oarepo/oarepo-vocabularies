#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Objects helping parent/hierarchy system fields management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_db import db
from invenio_vocabularies.records.api import Vocabulary

from oarepo_vocabularies.records.models import VocabularyHierarchy

if TYPE_CHECKING:
    from uuid import UUID

    from invenio_records.systemfields import DictField

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
        else:
            # there is no parent on record -> current is none and previous parent will be what we have in current
            self._previous_parent_uuid = self._parent_uuid
            self._parent_uuid = None
            self._parent_id = None
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

    def query_ancestors(self) -> Any:
        """Get all ancestors of this record."""
        ancestors_ids = self._hierarchy_data.get_ancestors_ids(self._record.id)
        return Vocabulary.get_records(ancestors_ids)

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

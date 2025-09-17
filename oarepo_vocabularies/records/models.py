#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabulary models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_db import db
from invenio_vocabularies.records.models import VocabularyMetadata
from sqlalchemy import literal, select
from sqlalchemy.orm import aliased
from sqlalchemy_utils.types import UUIDType

if TYPE_CHECKING:
    from uuid import UUID


class VocabularyHierarchy(db.Model):
    """Vocabulary hierarchy model."""

    __tablename__ = "vocabularies_hierarchy"

    id = db.Column(
        UUIDType,
        db.ForeignKey("vocabularies_metadata.id"),
        primary_key=True,
    )
    parent_id = db.Column(UUIDType, db.ForeignKey("vocabularies_hierarchy.id"), nullable=True)

    vocabulary_term = db.relationship(
        VocabularyMetadata,
        foreign_keys=[id],
        backref=db.backref(
            "hierarchy_metadata",
            uselist=False,
        ),
    )
    parent_hierarchy_metadata = db.relationship(
        "VocabularyHierarchy",
        foreign_keys=[parent_id],
        backref=db.backref("subterms", lazy="dynamic"),
        remote_side=[id],
    )

    pid = db.Column(db.String(255), nullable=False, unique=False)

    level: int = db.Column(db.Integer, default=1, nullable=False)

    titles: list = db.Column(db.JSON, default=list, nullable=False)

    ancestors: list = db.Column(db.JSON, default=list, nullable=False)

    ancestors_or_self: list = db.Column(db.JSON, default=list, nullable=False)

    leaf: bool = db.Column(db.Boolean, default=True, nullable=False)

    def fix_hierarchy_on_self(self) -> None:
        """Fix hierarchy data on this record based on its parent."""
        parent_hierarchy = self.parent_hierarchy_metadata

        # check if node has children
        result = db.session.query(VocabularyHierarchy.id).filter(VocabularyHierarchy.parent_id == self.id).all()

        new_leaf = not bool(result)
        title = self.titles[0]
        if not parent_hierarchy:
            new_titles = [title]
            new_ancestors = []
            new_ancestors_or_self = [self.pid]
            new_level = 1
        else:
            new_level = parent_hierarchy.level + 1
            new_titles = [title, *parent_hierarchy.titles]
            new_ancestors = parent_hierarchy.ancestors_or_self
            new_ancestors_or_self = [self.pid, *parent_hierarchy.ancestors_or_self]
        # Only update if something actually changed
        changed = (
            self.leaf != new_leaf
            or self.titles != new_titles
            or self.ancestors != new_ancestors
            or self.ancestors_or_self != new_ancestors_or_self
            or self.level != new_level
        )

        if changed:
            self.leaf = new_leaf
            self.titles = new_titles
            self.ancestors = new_ancestors
            self.ancestors_or_self = new_ancestors_or_self
            self.level = new_level
            db.session.add(self)

    @staticmethod
    def get_subterms_ids(start_id: UUID | None = None) -> list[UUID]:
        """Get all descendant IDs using recursive CTE."""
        # Base case: direct children of the node
        base = select(VocabularyHierarchy.id.label("id"), literal(1).label("depth")).where(
            VocabularyHierarchy.parent_id == start_id
        )

        # Recursive CTE
        hierarchy_cte = base.cte(name="children", recursive=True)
        child_alias = aliased(VocabularyHierarchy)

        recursive = select(child_alias.id, (hierarchy_cte.c.depth + 1).label("depth")).where(
            child_alias.parent_id == hierarchy_cte.c.id
        )

        hierarchy_cte = hierarchy_cte.union_all(recursive)

        # Final query with ORDER BY depth
        q = db.session.query(hierarchy_cte.c.id).order_by(hierarchy_cte.c.depth)
        return [cid for (cid,) in q.all() if cid is not None]

    @staticmethod
    def get_direct_subterms_ids(parent_id: UUID | None = None) -> list[UUID]:
        """Get direct subterms IDs."""
        result = db.session.query(VocabularyHierarchy.id).filter(VocabularyHierarchy.parent_id == parent_id).all()
        return [child_id for (child_id,) in result if child_id is not None]

    def fix_hierarchy_down(self) -> None:
        """Fix hierarchy for all descendants."""
        children_ids = VocabularyHierarchy.get_subterms_ids(self.id)

        for child in children_ids:
            child_hierarchy: VocabularyHierarchy = db.session.query(VocabularyHierarchy).get(child)  # type: ignore[assignment]
            child_hierarchy.fix_hierarchy_on_self()

    def update_leaf_status(self, force_child_exists: bool = False) -> None:
        """Update leaf status for the parent ancestor.

        :param force_child_exists: If True, forces the node to be non-leaf without checking the actual DB.
        """
        if force_child_exists:
            if self.leaf:
                self.leaf = False
                db.session.add(self)
            return

        is_leaf = not bool(VocabularyHierarchy.get_direct_subterms_ids(self.id))
        if is_leaf != self.leaf:
            self.leaf = is_leaf
            db.session.add(self)

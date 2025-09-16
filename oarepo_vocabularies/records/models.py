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

    from oarepo_vocabularies.records.systemfields.helpers import ParentObject


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

        self.leaf = not bool(result)
        title = self.titles[0]
        # TODO: check if something changed, if not, skip
        if not parent_hierarchy:
            self.titles = [title]
            self.ancestors = []
            self.ancestors_or_self = [self.pid]
            self.level = 1
        else:
            self.level = parent_hierarchy.level + 1
            self.titles = [title, *parent_hierarchy.titles]
            self.ancestors = parent_hierarchy.ancestors_or_self
            self.ancestors_or_self = [self.pid, *parent_hierarchy.ancestors_or_self]

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

    def fix_hierarchy_down_on_delete(self) -> None:
        """Fix hierarchy for all descendants."""
        children_ids = VocabularyHierarchy.get_subterms_ids(self.parent_id)

        for child in children_ids:
            if child == self.id:
                continue

            child_hierarchy: VocabularyHierarchy = db.session.query(VocabularyHierarchy).get(child)  # type: ignore[assignment]
            child_hierarchy.fix_hierarchy_on_self()

    def update_parent_leaf_status(self, cache: ParentObject) -> None:
        """Update leaf status for the parent ancestor."""
        parent_hierarchy = self.parent_hierarchy_metadata
        # case when record is deleted, change parent leaf if record has children
        if parent_hierarchy is not None and cache.previous_uuid != cache.uuid and not cache.uuid:
            previous_parent_rec = (
                db.session.query(VocabularyHierarchy).filter(VocabularyHierarchy.id == cache.previous_uuid).one()
            )

            parent_children = VocabularyHierarchy.get_direct_subterms_ids(previous_parent_rec.id)

            # since row in DB is not yet deleted, we need to exclude current record from children check
            parent_has_children = bool(
                len(parent_children) > 0  # list is not empty
                and any(child_id != self.id for child_id in parent_children)  # it has other children beside this record
            )

            if not previous_parent_rec.leaf and not parent_has_children:
                previous_parent_rec.leaf = True
                db.session.add(previous_parent_rec)

            return
        # current parent exists, change parent leaf if exists and if it is False
        if parent_hierarchy is not None and parent_hierarchy.leaf:
            parent_hierarchy.leaf = False  # type: ignore[attr-defined]
            db.session.add(parent_hierarchy)
            return

        # update previous parent, if current parent is none
        if parent_hierarchy is None and cache.previous_uuid:
            previous_parent_rec = (
                db.session.query(VocabularyHierarchy).filter(VocabularyHierarchy.id == cache.previous_uuid).one()
            )

            parent_has_children = bool(VocabularyHierarchy.get_direct_subterms_ids(previous_parent_rec.id))

            if not previous_parent_rec.leaf and not parent_has_children:
                previous_parent_rec.leaf = True
                db.session.add(previous_parent_rec)

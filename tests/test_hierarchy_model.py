# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

from invenio_vocabularies.records.models import VocabularyMetadata

from oarepo_vocabularies.records.models import VocabularyHierarchy


def test_db_hierarchy_model(db):
    parent = VocabularyMetadata(json={"id": "parent"})
    db.session.add(parent)
    db.session.commit()
    assert parent.id is not None
    assert parent.hierarchy_metadata is None

    parent_hierarchy = VocabularyHierarchy(id=parent.id, pid="eng")
    db.session.add(parent_hierarchy)
    db.session.commit()
    assert parent_hierarchy.vocabulary_term == parent

    child = VocabularyMetadata(json={"id": "child"})
    db.session.add(child)
    db.session.commit()
    assert child.id is not None
    child_hierarchy = VocabularyHierarchy(id=child.id, parent_id=parent.id, pid="eng-US")
    db.session.add(child_hierarchy)
    db.session.commit()

    assert child_hierarchy.parent_hierarchy_metadata == parent_hierarchy
    assert child_hierarchy.pid == "eng-US"
    assert child_hierarchy.vocabulary_term == child

    assert parent_hierarchy.subterms.count() == 1
    assert next(iter(parent_hierarchy.subterms)) == child_hierarchy

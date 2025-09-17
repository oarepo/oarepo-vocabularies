#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from typing import Any

import pytest
from flask_principal import PermissionDenied
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from marshmallow import ValidationError

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.records.models import VocabularyHierarchy
from oarepo_vocabularies.records.systemfields.hierarchy_system_field import (
    HierarchyPartSelector,
)


def test_hierarchy_change_leafs_after_insert(app, db, cache, lang_type, vocab_cf, search_clear):
    parent_data = {
        "id": "a",
        "title": {"en": "English", "da": "Engelsk"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello",
    }

    child_data_1 = {
        "id": "b",
        "title": {"en": "English (US)", "da": "Engelsk (US)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american",
        "parent": {"id": "a"},
    }

    child_data_2 = {
        "id": "c",
        "title": {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american texas yeehaw",
        "parent": {"id": "b"},
    }

    parent_rec = Vocabulary.create(data=parent_data)
    Vocabulary.pid.create(parent_rec)
    parent_rec.commit()
    db.session.commit()

    # check original hierarchy
    assert parent_rec.hierarchy.to_dict() == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": True,
        "parent": None,
    }

    child_rec_1 = Vocabulary.create(data=child_data_1)
    Vocabulary.pid.create(child_rec_1)
    child_rec_1.commit()
    db.session.commit()

    # check updated hierarchy after child creation
    parent_rec_updated = Vocabulary.get_record(parent_rec.id)
    assert parent_rec_updated.hierarchy.to_dict() == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": False,
        "parent": None,
    }
    assert child_rec_1.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,
        "parent": "a",
    }

    child_rec_2 = Vocabulary.create(data=child_data_2)
    Vocabulary.pid.create(child_rec_2)
    child_rec_2.commit()
    db.session.commit()

    # check updated hierarchy after another child creation
    parent_rec_updated_2 = Vocabulary.get_record(parent_rec.id)
    assert parent_rec_updated_2.hierarchy.to_dict() == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": False,
        "parent": None,
    }

    # check updated hierarchy after another child creation
    child_rec_updated = Vocabulary.get_record(child_rec_1.id)
    assert child_rec_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
        "parent": "a",
    }

    assert child_rec_2.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": True,
        "parent": "b",
    }


def create_vocabulary_graph(app, db, vocabulary_data, hierarchy):
    """Create a vocabulary graph based on the provided data and hierarchy.

    vocabulary_data: Dictionary mapping ID to vocabulary data
    hierarchy: Dictionary mapping ID to parent ID (None for root nodes)
    """
    created_records = {}

    # Sort by hierarchy - parents first, then children
    def get_depth(node_id) -> int:
        depth = 0
        current = node_id
        visited = set()
        while hierarchy.get(current) is not None and current not in visited:
            visited.add(current)
            current = hierarchy[current]
            depth += 1
        return depth

    # Sort IDs by depth (parents created before children)
    sorted_ids = sorted(vocabulary_data.keys(), key=get_depth)

    for vocab_id in sorted_ids:
        data = vocabulary_data[vocab_id].copy()

        # Add parent reference if it exists
        parent_id = hierarchy.get(vocab_id)
        if parent_id is not None:
            data["parent"] = {"id": parent_id}

        # Create and commit the record
        record = Vocabulary.create(data=data)
        Vocabulary.pid.create(record)
        record.commit()
        db.session.commit()

        created_records[vocab_id] = (record, data)

    return created_records


def test_hierarchy_change_parents_set_parent_to_existing(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d has new parent b -> update d
    d_rec, _ = results["d"]

    d_rec.parent.set("b")
    d_rec.commit()

    d_updated = Vocabulary.get_record(d_rec.id)
    assert d_updated["parent"]["id"] == "b"

    assert d_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["d", "b", "a"],
        "leaf": True,
        "parent": "b",
    }
    b_updated = Vocabulary.get_record(results["b"][0].id)

    b_children = VocabularyHierarchy.get_direct_subterms_ids(b_updated.id)
    assert len(b_children) == 2
    assert results["c"][0].id in b_children
    assert results["d"][0].id in b_children

    b_children = VocabularyHierarchy.get_subterms_ids(b_updated.id)
    assert len(b_children) == 2
    assert results["c"][0].id in b_children
    assert results["d"][0].id in b_children


def test_hierarchy_change_parents_set_parent_to_existing_as_leaf(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d has new parent c -> update d, c is not leaf
    d_rec, _ = results["d"]

    d_rec.parent.set("c")
    d_rec.commit()

    d_updated = Vocabulary.get_record(d_rec.id)
    assert d_updated["parent"]["id"] == "c"

    assert d_updated.hierarchy.to_dict() == {
        "level": 4,
        "titles": [
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["c", "b", "a"],
        "ancestors_or_self": ["d", "c", "b", "a"],
        "leaf": True,
        "parent": "c",
    }
    c_updated = Vocabulary.get_record(results["c"][0].id)

    assert c_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": False,
        "parent": "b",
    }

    c_children = VocabularyHierarchy.get_direct_subterms_ids(c_updated.id)
    assert len(c_children) == 1
    assert results["d"][0].id in c_children

    c_children = VocabularyHierarchy.get_subterms_ids(c_updated.id)
    assert len(c_children) == 1
    assert results["d"][0].id in c_children


def test_hierarchy_change_parents_set_parent_to_none(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: c has no parent -> update c and b is leaf
    c_rec, _ = results["c"]

    b_rec = Vocabulary.get_record(results["b"][0].id)

    assert b_rec.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
        "parent": "a",
    }

    c_rec.parent.set(None)
    c_rec.commit()

    c_updated = Vocabulary.get_record(c_rec.id)
    assert c_updated["parent"] is None

    assert c_updated.hierarchy.to_dict() == {
        "level": 1,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
        ],
        "ancestors": [],
        "ancestors_or_self": ["c"],
        "leaf": True,
        "parent": None,
    }
    b_updated = Vocabulary.get_record(results["b"][0].id)

    assert b_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,  # changed from false
        "parent": "a",
    }

    c_children = VocabularyHierarchy.get_direct_subterms_ids(c_updated.id)
    assert len(c_children) == 0

    b_children = VocabularyHierarchy.get_direct_subterms_ids(b_updated.id)
    assert len(b_children) == 0


def test_hierarchy_change_parents_set_new_root_parent(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d becomes parent of a -> update everything below a
    a_rec, _ = results["a"]

    a_rec.parent.set("d")
    a_rec.commit()

    a_updated = Vocabulary.get_record(a_rec.id)
    assert a_updated["parent"] == {"id": "d"}

    assert a_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English", "da": "Engelsk"},  # a
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
        ],
        "ancestors": ["d"],
        "ancestors_or_self": ["a", "d"],
        "leaf": False,
        "parent": "d",
    }

    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
            {"en": "English (UK)", "da": "Engelsk (UK)"},
        ],
        "ancestors": ["a", "d"],
        "ancestors_or_self": ["b", "a", "d"],
        "leaf": False,
        "parent": "a",
    }

    c_updated = Vocabulary.get_record(results["c"][0].id)
    assert c_updated.hierarchy.to_dict() == {
        "level": 4,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
        ],
        "ancestors": ["b", "a", "d"],
        "ancestors_or_self": ["c", "b", "a", "d"],
        "leaf": True,
        "parent": "b",
    }


def test_hierarchy_delete_record(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: c is deleted -> update leaf status b
    c_rec, _ = results["c"]

    c_rec.delete()

    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,  # changed from false
        "parent": "a",
    }

    # check DB table
    entries = VocabularyHierarchy.query.filter_by(id=c_rec.id).all()
    assert len(entries) == 0

    # check that B has no children
    b_children = VocabularyHierarchy.get_direct_subterms_ids(b_updated.id)
    assert len(b_children) == 0

    # check that A has no C as subterm
    a_children = VocabularyHierarchy.get_subterms_ids(results["a"][0].id)
    assert len(a_children) == 1  # only B


def test_hierarchy_delete_record_with_children(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # We want to delete B, but it has child C, should raise error
    b_rec, _ = results["b"]
    with pytest.raises(
        ValidationError,
        match=r"Cannot delete a vocabulary term with ID .* that has children. Reassign or delete children first.",
    ):
        b_rec.delete()

    c_updated = Vocabulary.get_record(results["c"][0].id)
    assert c_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": True,
        "parent": "b",
    }

    # check DB table
    entries = VocabularyHierarchy.query.filter_by(id=b_rec.id).all()
    assert len(entries) == 1  # still there

    # check that B still has children
    b_children = VocabularyHierarchy.get_direct_subterms_ids(results["b"][0].id)
    assert len(b_children) == 1  # only C

    # check that A subterms
    a_children = VocabularyHierarchy.get_subterms_ids(results["a"][0].id)
    assert len(a_children) == 2  # B and C


def test_hierarchy_delete_root_with_children(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    vocabulary_data, _ = lang_data3
    hierarchy = {
        "a": None,  # root node
        "b": "a",  # b's parent is a
        "c": "b",  # c's parent is b
        "d": "c",  # d's parent is c
    }

    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a -> b -> c -> d
    # We want to delete A, which is parent of B, C, D, should raise error

    # Check initial hierarchy
    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
        "parent": "a",
    }
    c_updated = Vocabulary.get_record(results["c"][0].id)
    assert c_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": False,
        "parent": "b",
    }

    d_updated = Vocabulary.get_record(results["d"][0].id)
    assert d_updated.hierarchy.to_dict() == {
        "level": 4,
        "titles": [
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["c", "b", "a"],
        "ancestors_or_self": ["d", "c", "b", "a"],
        "leaf": True,
        "parent": "c",
    }

    a_rec, _ = results["a"]
    with pytest.raises(
        ValidationError,
        match=r"Cannot delete a vocabulary term with ID .* that has children. Reassign or delete children first.",
    ):
        a_rec.delete()

    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
        "parent": "a",
    }
    c_updated = Vocabulary.get_record(results["c"][0].id)
    assert c_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": False,
        "parent": "b",
    }

    d_updated = Vocabulary.get_record(results["d"][0].id)
    assert d_updated.hierarchy.to_dict() == {
        "level": 4,
        "titles": [
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["c", "b", "a"],
        "ancestors_or_self": ["d", "c", "b", "a"],
        "leaf": True,
        "parent": "c",
    }

    # check DB table
    entries = VocabularyHierarchy.query.filter_by(id=results["a"][0].id).all()
    assert len(entries) == 1

    # check that A has 1 child B
    a_children = VocabularyHierarchy.get_direct_subterms_ids(results["a"][0].id)
    assert len(a_children) == 1


def test_hierarchy_change_parents_move_under_other_branch(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, _ = lang_data3
    hierarchy = {
        "a": None,  # root node
        "b": "a",  # b's parent is a
        "c": "b",  # c's parent is b
        "d": "a",  # d's parent is a
    }

    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    #                           -> d
    # After changes: d becomes parent of c -> b is leaf, d is not leaf, c is updated

    c_rec, _ = results["c"]

    c_rec.parent.set("d")
    assert c_rec.parent.id == "d"
    assert c_rec.parent.previous_id == "b"
    c_rec.commit()

    c_updated = Vocabulary.get_record(c_rec.id)
    assert c_updated.hierarchy.to_dict() == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["d", "a"],
        "ancestors_or_self": ["c", "d", "a"],
        "leaf": True,
        "parent": "d",
    }
    d_updated = Vocabulary.get_record(results["d"][0].id)
    assert d_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["d", "a"],
        "leaf": False,  # changed from true
        "parent": "a",
    }

    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,  # changed from false
        "parent": "a",
    }


def test_parent_object_change_of_parent_ids(app, db, cache, lang_type, vocab_cf, search_clear, lang_data3):
    parent_data = {
        "id": "a",
        "title": {"en": "English", "da": "Engelsk"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello",
    }

    child_data_1 = {
        "id": "b",
        "title": {"en": "English (US)", "da": "Engelsk (US)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american",
        "parent": {"id": "a"},
    }

    child_data_2 = {
        "id": "c",
        "title": {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american texas yeehaw",
    }

    child_data_3 = {
        "id": "d",
        "title": {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american texas yeehaw",
    }

    parent_rec = Vocabulary.create(data=parent_data)
    Vocabulary.pid.create(parent_rec)
    parent_rec.commit()
    db.session.commit()

    child_rec_1 = Vocabulary.create(data=child_data_1)
    Vocabulary.pid.create(child_rec_1)
    assert child_rec_1.parent.id == "a"
    child_rec_1.commit()
    db.session.commit()

    child_rec_2 = Vocabulary.create(data=child_data_2)
    Vocabulary.pid.create(child_rec_2)
    assert child_rec_2.parent.id is None
    child_rec_2.parent.set("a")
    assert child_rec_2.parent.id == "a"

    child_data_3 = Vocabulary.create(data=child_data_3)
    Vocabulary.pid.create(child_data_3)
    assert child_data_3.parent.id is None
    child_data_3.parent = "a"
    assert child_data_3.parent.id == "a"

    child_rec_1.parent = "b"
    assert child_rec_1.parent.id == "b"
    assert child_rec_1.parent.previous_id == "a"


def test_hierarchy_lang(app, db, cache, lang_type, lang_data, lang_data_child, vocab_cf, search_clear):
    parent = vocab_service.create(system_identity, lang_data)
    assert "parent" not in parent.links

    assert parent._record.hierarchy.to_dict() == {  # noqa: SLF001
        "level": 1,
        "titles": [{"cs": "Angličtina", "da": "Engelsk", "en": "English"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
        "parent": None,
    }

    child = vocab_service.create(system_identity, lang_data_child)

    assert child.links["parent"] == "https://127.0.0.1:5000/api/vocabularies/languages/eng"
    assert parent.links["children"] == "https://127.0.0.1:5000/api/vocabularies/languages?h-parent=eng"
    assert parent.links["descendants"] == "https://127.0.0.1:5000/api/vocabularies/languages?h-ancestor=eng"
    assert child._record.hierarchy.to_dict() == {  # noqa: SLF001
        "level": 2,
        "titles": [
            {
                "cs": "Angličtina (Spojené státy)",
                "da": "Engelsk (US)",
                "en": "English (US)",
            },
            {"cs": "Angličtina", "da": "Engelsk", "en": "English"},
        ],
        "ancestors": ["eng"],
        "ancestors_or_self": ["eng.US", "eng"],
        "leaf": True,
        "parent": "eng",
    }


def test_children(sample_records, client, search_clear):
    def _test_children(x) -> None:
        node, expected_children = x
        children_url = node["links"]["children"]
        resp = client.get(children_url).json
        if "hits" not in resp:
            raise AssertionError(f"Hits not in {resp}")
        child_nodes = resp["hits"]["hits"]
        expected_ids = {c.node["id"] for c in expected_children}
        actual_ids = {x["id"] for x in child_nodes}
        assert expected_ids == actual_ids, (
            f"Children are not as expected. Expected {expected_ids}, got {actual_ids} on url {children_url}"
        )

        for child in expected_children:
            _test_children(child)

    for s in sample_records:
        _test_children(s)


def test_descendants(sample_records, client, search_clear):
    def _get_descendants(x) -> Any:
        for c in x.children:
            yield c
            yield from _get_descendants(c)

    def _test_descendants(x) -> None:
        node = x.node
        descendants_url = node["links"]["descendants"]
        resp = client.get(descendants_url).json
        if "hits" not in resp:
            raise AssertionError(f"Hits not in {resp}")
        child_nodes = resp["hits"]["hits"]
        expected_ids = {a.node["id"] for a in _get_descendants(x)}
        actual_ids = {x["id"] for x in child_nodes}
        assert expected_ids == actual_ids, (
            f"Children are not as expected. Expected {expected_ids}, got {actual_ids} on url {descendants_url}"
        )

        for child in x.children:
            _test_descendants(child)

    for s in sample_records:
        _test_descendants(s)


def test_parent(sample_records, client, search_clear):
    def _test_parent(x, expected_parent) -> None:
        node = x.node
        if expected_parent:
            parent_url = node["links"]["parent"]
            resp = client.get(parent_url).json
            assert resp["id"] == expected_parent["id"], (
                f"Expected and actual parents do not match. Expected {expected_parent['id']}, got {resp['id']}"
            )
        else:
            assert "parent" not in node["links"]
        for child in x.children:
            _test_parent(child, x.node)

    for s in sample_records:
        _test_parent(s, None)


def test_hierarchy_selector():
    data = {
        "authority": {
            "@v": "95bcf144-e477-4888-b7ba-68555090d01f::1",
            "id": "03zsq2967",
            "title": {"en": "Association of Asian Pacific Community Health Organizations"},
            "hierarchy": {
                "ancestors_or_self": ["03zsq2967", "11111"],
                "title": [
                    {"en": "Association of Asian Pacific Community Health Organizations"},
                    {"en": "AAAAA"},
                ],
            },
        }
    }
    assert HierarchyPartSelector("authority", level=0).select(data) == [{"id": "11111", "title": {"en": "AAAAA"}}]
    assert HierarchyPartSelector("authority", level=1).select(data) == [
        {
            "id": "03zsq2967",
            "title": {"en": "Association of Asian Pacific Community Health Organizations"},
        }
    ]


def test_leaf(app, db, cache, lang_type, vocab_cf, search_clear):
    parent = vocab_service.create(system_identity, {"id": "eng", "title": {"en": "English"}, "type": "languages"})
    assert "parent" not in parent.links
    assert parent.data["hierarchy"]["leaf"]

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data

    assert parent_data["hierarchy"]["leaf"]

    child = vocab_service.create(
        system_identity,
        {
            "id": "eng.US",
            "title": {"en": "English (US)"},
            "hierarchy": {"parent": "eng"},
            "type": "languages",
        },
    )

    assert child.data["hierarchy"]["leaf"]

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data
    assert not parent_data["hierarchy"]["leaf"]

    vocab_service.delete(system_identity, id_=("languages", child.id))

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data
    assert parent_data["hierarchy"]["leaf"]


def test_update_with_disallowed_hierarchy(
    app, db, cache, lang_type, sample_records, vocab_cf, search_clear, identity_simple
):
    with pytest.raises(PermissionDenied):
        vocab_service.update(
            identity_simple,
            ("languages", "eng.UK.S"),
            {
                "hierarchy": {"parent": "eng"},
                "type": "languages",
                "title": {"en": "English (UK)"},
            },
        )


def test_update_with_hierarchy_change(app, db, cache, lang_type, sample_records, vocab_cf, search_clear):
    vocab_service.update(
        system_identity,
        ("languages", "eng.UK.S"),
        {
            "hierarchy": {"parent": "eng"},
            "type": "languages",
            "title": {"en": "English (UK)"},
        },
    )

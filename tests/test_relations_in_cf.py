from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.records.models import VocabularyHierarchy


def test_extra_cf(app, db, cache, lang_type, vocab_cf, search_clear):
    parent_data = {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello",
    }

    child_data = {
        "id": "eng-us",
        "title": {"en": "English (US)", "da": "Engelsk (US)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american",
        "parent": {"id": "eng"},
    }

    parent_rec = Vocabulary.create(data=parent_data)
    Vocabulary.pid.create(parent_rec)
    parent_rec.commit()
    db.session.commit()

    assert parent_rec.hierarchy.data == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
    }

    child_rec = Vocabulary.create(data=child_data)
    Vocabulary.pid.create(child_rec)
    child_rec.commit()
    db.session.commit()

    print(dict(child_rec))
    parent_uuid = parent_rec.id
    child_uuid = child_rec.id

    # check DB table
    entries = VocabularyHierarchy.query.filter_by(
        id=child_uuid, parent_id=parent_uuid
    ).all()

    assert len(entries) == 1

    assert child_rec.hierarchy.data == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["eng"],
        "ancestors_or_self": ["eng-us", "eng"],
        "leaf": True,
    }

    # check the updated hierarchy
    parent_rec = Vocabulary.get_record(parent_rec.id)
    assert parent_rec.hierarchy.data == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": False,
    }

    # check child_rec ma title v parent


def test_hierarchy_change_leafs(app, db, cache, lang_type, vocab_cf, search_clear):
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
    assert parent_rec.hierarchy.data == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": True,
    }

    child_rec_1 = Vocabulary.create(data=child_data_1)
    Vocabulary.pid.create(child_rec_1)
    child_rec_1.commit()
    db.session.commit()

    # check updated hierarchy after child creation
    parent_rec_updated = Vocabulary.get_record(parent_rec.id)
    assert parent_rec_updated.hierarchy.data == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": False,
    }
    assert child_rec_1.hierarchy.data == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,
    }

    child_rec_2 = Vocabulary.create(data=child_data_2)
    Vocabulary.pid.create(child_rec_2)
    child_rec_2.commit()
    db.session.commit()

    # check updated hierarchy after another child creation
    parent_rec_updated_2 = Vocabulary.get_record(parent_rec.id)
    assert parent_rec_updated_2.hierarchy.data == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["a"],
        "leaf": False,
    }

    # check updated hierarchy after another child creation
    child_rec_updated = Vocabulary.get_record(child_rec_1.id)
    assert child_rec_updated.hierarchy.data == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
    }

    assert child_rec_2.hierarchy.data == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": True,
    }


def prepare_data(app, db):
    parent_data = {
        "id": "a",
        "title": {"en": "English", "da": "Engelsk"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello",
    }

    parent_data_2 = {
        "id": "d",
        "title": {"en": "English (UK)", "da": "Engelsk (UK)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in UK",
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

    # prepare and create record
    parent_rec = Vocabulary.create(data=parent_data)
    Vocabulary.pid.create(parent_rec)
    parent_rec.commit()
    db.session.commit()

    parent_rec_2 = Vocabulary.create(data=parent_data_2)
    Vocabulary.pid.create(parent_rec_2)
    parent_rec_2.commit()
    db.session.commit()

    child_rec_1 = Vocabulary.create(data=child_data_1)
    Vocabulary.pid.create(child_rec_1)
    child_rec_1.commit()
    db.session.commit()

    child_rec_2 = Vocabulary.create(data=child_data_2)
    Vocabulary.pid.create(child_rec_2)
    child_rec_2.commit()
    db.session.commit()

    return [
        (parent_rec, parent_data),
        (parent_rec_2, parent_data_2),
        (child_rec_1, child_data_1),
        (child_rec_2, child_data_2),
    ]


def create_vocabulary_graph(app, db, vocabulary_data, hierarchy):
    """
    vocabulary_data: Dictionary mapping ID to vocabulary data
    hierarchy: Dictionary mapping ID to parent ID (None for root nodes)
    """
    created_records = {}

    # Sort by hierarchy - parents first, then children
    def get_depth(node_id):
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


def test_hierarchy_change_parents_option1(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d has new parent b -> update d
    d_rec, d_data = results["d"]

    d_rec.parent.set({"id": "b"})
    d_rec.commit()

    d_updated = Vocabulary.get_record(d_rec.id)
    assert d_updated["parent"]["id"] == "b"

    assert (
        d_updated["hierarchy"]
        == d_updated.hierarchy.data
        == {
            "level": 3,
            "titles": [
                {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
                {"en": "English (US)", "da": "Engelsk (US)"},  # b
                {"en": "English", "da": "Engelsk"},  # a
            ],
            "ancestors": ["b", "a"],
            "ancestors_or_self": ["d", "b", "a"],
            "leaf": True,
        }
    )
    b_updated = Vocabulary.get_record(results["b"][0].id)

    b_children = b_updated.hierarchy._get_direct_children()
    assert len(b_children) == 2
    assert results["c"][0].id in b_children
    assert results["d"][0].id in b_children

    b_children = b_updated.hierarchy._get_all_children()
    assert len(b_children) == 2
    assert results["c"][0].id in b_children
    assert results["d"][0].id in b_children


def test_hierarchy_change_parents_option2(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d has new parent c -> update d, c is not leaf
    d_rec, d_data = results["d"]

    d_rec.parent.set({"id": "c"})
    d_rec.commit()

    d_updated = Vocabulary.get_record(d_rec.id)
    assert d_updated["parent"]["id"] == "c"

    assert (
        d_updated["hierarchy"]
        == d_updated.hierarchy.data
        == {
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
        }
    )
    c_updated = Vocabulary.get_record(results["c"][0].id)

    c_updated.hierarchy.data == {
        "level": 3,
        "titles": [
            {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["b", "a"],
        "ancestors_or_self": ["c", "b", "a"],
        "leaf": False,
    }

    c_children = c_updated.hierarchy._get_direct_children()
    assert len(c_children) == 1
    assert results["d"][0].id in c_children

    c_children = c_updated.hierarchy._get_all_children()
    assert len(c_children) == 1
    assert results["d"][0].id in c_children


def test_hierarchy_change_parents_option3(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: c has no parent -> update c and b is leaf
    c_rec, c_data = results["c"]

    b_rec = Vocabulary.get_record(results["b"][0].id)

    assert b_rec.hierarchy.data == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": False,
    }

    c_rec.parent.set({})
    c_rec.commit()

    c_updated = Vocabulary.get_record(c_rec.id)
    assert c_updated["parent"] == {}

    assert (
        c_updated["hierarchy"]
        == c_updated.hierarchy.data
        == {
            "level": 1,
            "titles": [
                {"en": "English (US Texas)", "da": "Engelsk (US Texas)"},  # c
            ],
            "ancestors": [],
            "ancestors_or_self": ["c"],
            "leaf": True,
        }
    )
    b_updated = Vocabulary.get_record(results["b"][0].id)

    assert b_updated.hierarchy.data == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
        ],
        "ancestors": ["a"],
        "ancestors_or_self": ["b", "a"],
        "leaf": True,  # changed from false
    }

    c_children = c_updated.hierarchy._get_direct_children()
    assert len(c_children) == 0

    b_children = b_updated.hierarchy._get_direct_children()
    assert len(b_children) == 0


def test_hierarchy_change_parents_option4(
    app, db, cache, lang_type, vocab_cf, search_clear, lang_data3
):
    vocabulary_data, hierarchy = lang_data3
    results = create_vocabulary_graph(app, db, vocabulary_data, hierarchy)
    # Starting graph:
    # 1. a (root = main parent) -> b (second parent) -> c
    # 2. d
    # After changes: d becomes parent of a -> update everything below a
    a_rec, a_data = results["a"]

    a_rec.parent.set({"id": "d"})
    a_rec.commit()

    a_updated = Vocabulary.get_record(a_rec.id)
    assert a_updated["parent"] == {"id": "d"}

    assert (
        a_updated["hierarchy"]
        == a_updated.hierarchy.data
        == {
            "level": 2,
            "titles": [
                {"en": "English", "da": "Engelsk"},  # a
                {"en": "English (UK)", "da": "Engelsk (UK)"},  # d
            ],
            "ancestors": ["d"],
            "ancestors_or_self": ["a", "d"],
            "leaf": False,
        }
    )

    b_updated = Vocabulary.get_record(results["b"][0].id)
    assert b_updated.hierarchy.data == {
        "level": 3,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},  # b
            {"en": "English", "da": "Engelsk"},  # a
            {"en": "English (UK)", "da": "Engelsk (UK)"},
        ],
        "ancestors": ["a", "d"],
        "ancestors_or_self": ["b", "a", "d"],
        "leaf": False,
    }

    c_updated = Vocabulary.get_record(results["c"][0].id)
    assert c_updated.hierarchy.data == {
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
    }

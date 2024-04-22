from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service

from oarepo_vocabularies.records.systemfields import HierarchyPartSelector


def test_hierarchy_lang(
    app, db, cache, lang_type, lang_data, lang_data_child, vocab_cf
):
    parent = vocab_service.create(system_identity, lang_data)
    assert "parent" not in parent.links

    assert parent.data["hierarchy"] == {
        "level": 1,
        "title": [{"cs": "Angličtina", "da": "Engelsk", "en": "English"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
    }

    child = vocab_service.create(system_identity, lang_data_child)
    assert (
        child.links["parent"] == "https://127.0.0.1:5000/api/vocabularies/languages/eng"
    )
    assert (
        parent.links["children"]
        == "https://127.0.0.1:5000/api/vocabularies/languages?h-parent=eng"
    )
    assert (
        parent.links["descendants"]
        == "https://127.0.0.1:5000/api/vocabularies/languages?h-ancestor=eng"
    )
    assert child.data["hierarchy"] == {
        "level": 2,
        "parent": "eng",
        "title": [
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
    }


def test_children(sample_records, client):
    def _test_children(x):
        node, expected_children = x
        children_url = node["links"]["children"]
        resp = client.get(children_url).json
        if "hits" not in resp:
            raise AssertionError(f"Hits not in {resp}")
        child_nodes = resp["hits"]["hits"]
        expected_ids = set(c.node["id"] for c in expected_children)
        actual_ids = set(x["id"] for x in child_nodes)
        assert (
            expected_ids == actual_ids
        ), f"Children are not as expected. Expected {expected_ids}, got {actual_ids} on url {children_url}"

        for child in expected_children:
            _test_children(child)

    for s in sample_records:
        _test_children(s)


def test_descendants(sample_records, client):
    def _get_descendants(x):
        for c in x.children:
            yield c
            yield from _get_descendants(c)

    def _test_descendants(x):
        node = x.node
        descendants_url = node["links"]["descendants"]
        resp = client.get(descendants_url).json
        if "hits" not in resp:
            raise AssertionError(f"Hits not in {resp}")
        child_nodes = resp["hits"]["hits"]
        expected_ids = set(a.node["id"] for a in _get_descendants(x))
        actual_ids = set(x["id"] for x in child_nodes)
        assert (
            expected_ids == actual_ids
        ), f"Children are not as expected. Expected {expected_ids}, got {actual_ids} on url {descendants_url}"

        for child in x.children:
            _test_descendants(child)

    for s in sample_records:
        _test_descendants(s)


def test_parent(sample_records, client):
    def _test_parent(x, expected_parent):
        node = x.node
        if expected_parent:
            parent_url = node["links"]["parent"]
            resp = client.get(parent_url).json
            assert (
                resp["id"] == expected_parent["id"]
            ), f"Expected and actual parents do not match. Expected {expected_parent['id']}, got {resp['id']}"
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
            "title": {
                "en": "Association of Asian Pacific Community Health Organizations"
            },
            "hierarchy": {
                "ancestors_or_self": ["03zsq2967", "11111"],
                "title": [
                    {
                        "en": "Association of Asian Pacific Community Health Organizations"
                    },
                    {"en": "AAAAA"},
                ],
            },
        }
    }
    assert HierarchyPartSelector("authority", level=0).select(data) == [
        {"id": "11111", "title": {"en": "AAAAA"}}
    ]
    assert HierarchyPartSelector("authority", level=1).select(data) == [
        {
            "id": "03zsq2967",
            "title": {
                "en": "Association of Asian Pacific Community Health " "Organizations"
            },
        }
    ]


def test_leaf(app, db, cache, lang_type, vocab_cf):
    parent = vocab_service.create(
        system_identity, {"id": "eng", "title": {"en": "English"}, "type": "languages"}
    )
    assert "parent" not in parent.links
    assert parent.data["hierarchy"]["leaf"] == True

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data

    assert parent_data["hierarchy"]["leaf"] == True

    child = vocab_service.create(
        system_identity,
        {
            "id": "eng.US",
            "title": {"en": "English (US)"},
            "hierarchy": {"parent": "eng"},
            "type": "languages",
        },
    )

    assert child.data["hierarchy"]["leaf"] == True

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data
    assert parent_data["hierarchy"]["leaf"] == False

    vocab_service.delete(system_identity, id_=("languages", child.id))

    vocab_service.indexer.refresh()
    parent_data = vocab_service.read(system_identity, ("languages", parent.id)).data
    assert parent_data["hierarchy"]["leaf"] == True

from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_access.permissions import system_identity


def test_hierarchy_lang(
    app, db, cache, lang_type, lang_data, lang_data_child, vocab_cf
):
    parent = vocab_service.create(system_identity, lang_data)
    assert "parent" not in parent.links

    assert parent.data["hierarchy"] == {
        "level": 1,
        "title": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
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
            {"da": "Engelsk (US)", "en": "English (US)"},
            {"da": "Engelsk", "en": "English"},
        ],
        "ancestors": ["eng"],
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

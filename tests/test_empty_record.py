# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations


def test_empty_record(app, vocabularies_ui_resource):
    assert vocabularies_ui_resource.empty_record(vocabulary_type="test") == {
        "created": None,
        "description": {},
        "hierarchy": {
            "ancestors": [],
            "ancestors_or_self": [],
            "level": None,
            "parent": "",
            "titles": [],
            "leaf": None,
        },
        "custom_fields": {
            "blah": "",
            "relatedURI": {},
            "hint": {},
            "nonpreferredLabels": [],
        },
        "icon": "",
        "id": "",
        "links": None,
        "props": {},
        "revision_id": None,
        "tags": [],
        "title": {},
        "type": "test",
        "mappings": [],
        "updated": None,
    }

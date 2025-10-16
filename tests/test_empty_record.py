#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations


def test_empty_record(app, vocabularies_ui_resource):
    assert vocabularies_ui_resource.empty_record(type="test") == {
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
        "updated": None,
        "expanded": {},
        "files": {"enabled": None},
        "pids": {},
        "status": "draft",
    }

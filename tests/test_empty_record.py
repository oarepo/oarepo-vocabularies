#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import pytest
from flask_resources.context import ResourceRequestCtx


@pytest.mark.skip(
    reason="AttributeError: 'Cfg' object has no attribute 'model_name' in oarepo_ui/resources/records/config.py"
)
def test_empty_record(app, vocabularies_ui_resource, vocabularies_ui_resource_config):
    ctx = ResourceRequestCtx(vocabularies_ui_resource_config)
    ctx.view_args = {"vocabulary_type": "test"}
    with ctx:
        assert vocabularies_ui_resource.empty_record(resource_requestctx=ctx) == {
            "blah": "",
            "created": None,
            "description": {},
            "hierarchy": {
                "ancestors": [],
                "ancestors_or_self": [],
                "level": None,
                "parent": "",
                "title": [],
                "leaf": None,
            },
            "hint": {},
            "icon": "",
            "id": "",
            "links": None,
            "nonpreferredLabels": [],
            "props": {},
            "relatedURI": {},
            "revision_id": None,
            "tags": [],
            "title": {},
            "type": "test",
            "updated": None,
        }

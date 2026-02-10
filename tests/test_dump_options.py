#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from invenio_records_resources.services.records.results import RecordItem

from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from tests.simple_model import ModelRecord


def test_dump_options(
    sample_records,
    simple_record_service,
    simple_record_ui_resource,
    search_clear,
    identity,
):
    comp = DepositVocabularyOptionsComponent(resource=simple_record_ui_resource)
    form_config = {}
    rec = ModelRecord({})
    comp.form_config(
        api_record=RecordItem(
            service=simple_record_service, identity=identity, record=rec
        ),
        record=None,
        identity=identity,
        form_config=form_config,
        ui_links={},
        extra_context={},
    )

    form_config_vocabularies = form_config["vocabularies"]
    assert form_config_vocabularies["authority"] == {
        "definition": {"title": {"en": "authority"}, "authority": "TODO"},
        "url": "/api/vocabularies/authority",
    }
    assert form_config_vocabularies["creator"] == {
        "definition": {},
        "url": "/api/vocabularies/creator",
    }
    assert form_config_vocabularies["award"] == {
        "definition": {},
        "url": "/api/vocabularies/award",
    }
    assert form_config_vocabularies["ror-authority"] == {
        "definition": {
            "authority": "TODO",
            "title": {"en": "ROR Authority"},
        },
        "url": "/api/vocabularies/ror-authority",
    }
    assert form_config_vocabularies["languages"]["definition"] == {
        "title": {"cs": "jazyky", "en": "languages"},
        "description": {
            "cs": "slovnikovy typ ceskeho jazyka.",
            "en": "czech language vocabulary type.",
        },
        "dump_options": True,
        "custom_fields": ["relatedURI"],
        "props": {
            "alpha3CodeNative": {
                "description": "ISO 639-2 standard 3-letter language code",
                "icon": None,
                "label": "Alpha3 code (native)",
                "multiple": False,
                "options": [],
                "placeholder": "eng, ces...",
            }
        },
    }

    assert len(form_config_vocabularies["languages"]["all"]) == 4
    ids_ = ["eng.UK.S", "eng.UK", "eng.US", "eng"]
    for i in form_config_vocabularies["languages"]["all"]:
        assert i["value"] in ids_
        if i["value"] in ["eng", "eng.UK"]:
            assert i["element_type"] == "parent"
        elif i["value"] in ["eng.UK.S", "eng.US"]:
            assert i["element_type"] == "leaf"

    assert len(form_config_vocabularies["languages"]["featured"]) == 1
    assert (
        next(iter(form_config_vocabularies["languages"]["featured"]))["value"]
        == "eng.UK.S"
    )

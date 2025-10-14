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
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service

from oarepo_vocabularies.records.api import Vocabulary
from tests.test_uidetail import remove_ws


@pytest.mark.skip(reason="Later will be implemented as administration view")
def test_uiedit(
    client_with_credentials,
    app,
    db,
    cache,
    lang_type,
    lang_data,
    vocab_cf,
    fake_manifest,
    search_clear,
    clear_vocabulary_permissions,
):
    for _id in range(100):
        vocab_service.create(
            system_identity,
            {
                **lang_data,
                "id": str(_id),
            },
        )
    Vocabulary.index.refresh()
    edit_page = client_with_credentials.get("/vocabularies/languages/1/edit")
    assert edit_page.status_code == 200
    # dont know what is supposed to be in assert and edit page
    assert remove_ws(""""https://127.0.0.1:5000/vocabularies/languages/1""") in remove_ws(edit_page.text)


@pytest.mark.skip(reason="need loading fixtures")
def test_uiedit_locale(
    client_with_credentials,
    app,
    db,
    cache,
    vocab_cf,
    fake_manifest,
    reset_babel,
    search_clear,
):
    # load fixtures here...
    Vocabulary.index.refresh()

    reset_babel()
    edit_page = client_with_credentials.get("/vocabularies/languages/en/edit", headers=[("Accept-Language", "cs")])
    assert remove_ws(
        """
"languages": {"all": [
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["Angli\\u010dtina"]}, "text": "Angli\\u010dtina", "value": "en"},
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["\\u010ce\\u0161tina"]}, "text": "\\u010ce\\u0161tina", "value": "cs"}
        """  # noqa: E501
    ) in remove_ws(edit_page.text)

    reset_babel()
    edit_page = client_with_credentials.get("/vocabularies/languages/en/edit", headers=[("Accept-Language", "en")])
    assert remove_ws(
        """
"languages": {"all": [
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["Czech"]}, "text": "Czech", "value": "cs"},
{"element_type": "leaf", "hierarchy": {"ancestors": [], "title": ["English"]}, "text": "English", "value": "en"}
"""
    ) in remove_ws(edit_page.text)

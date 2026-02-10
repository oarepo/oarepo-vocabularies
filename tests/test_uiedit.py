#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pytest
from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AuthenticatedUser,
)

from oarepo_vocabularies.records.api import Vocabulary
from tests.test_uidetail import remove_ws

if TYPE_CHECKING:
    from invenio_records_permissions.generators import Generator as InvenioGenerator


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


def test_edit_permission_denied(
    vocabularies_ui_resource,
    identity,
    logged_in_client,
    fake_manifest,
    app,
    clear_vocabulary_permissions,
    db,
    cache,
    search_clear,
    client,
    vocab_cf,
    lang_data_many,
):
    response = logged_in_client.get("/vocabularies/languages/fr/edit")
    assert response.status_code == 403


class TestPermissionPolicy(RecordPermissionPolicy):
    """Policy that allows updating to authenticated user."""

    can_update: ClassVar[list[InvenioGenerator]] = [AuthenticatedUser()]


def test_uiedit(
    app,
    vocabularies_ui_resource,
    identity,
    logged_in_client,
    fake_manifest,
    db,
    cache,
    search_clear,
    client,
    vocab_cf,
    lang_data_many,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = TestPermissionPolicy

    response = logged_in_client.get("/vocabularies/languages/fr/edit")
    assert response.status_code == 200
    page_text = response.text
    assert "vocabularyProps" in page_text
    assert "vocabularyType" in page_text

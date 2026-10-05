# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AuthenticatedUser,
)

if TYPE_CHECKING:
    from invenio_records_permissions.generators import Generator as InvenioGenerator


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

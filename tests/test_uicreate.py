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

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AuthenticatedUser,
)

if TYPE_CHECKING:
    from invenio_records_permissions.generators import Generator as InvenioGenerator


def test_create_permission_denied(
    vocabularies_ui_resource,
    identity,
    lang_type,
    logged_in_client,
    fake_manifest,
    clear_vocabulary_permissions,
):
    # Simulate permission denied
    response = logged_in_client.get("/vocabularies/languages/_new")
    assert response.status_code == 403


class TestPermissionPolicy(RecordPermissionPolicy):
    """Policy that allows creation to authenticated user."""

    can_create: ClassVar[list[InvenioGenerator]] = [AuthenticatedUser()]


def test_uicreate(
    app,
    vocabularies_ui_resource,
    identity,
    lang_type,
    logged_in_client,
    fake_manifest,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = TestPermissionPolicy

    response = logged_in_client.get("/vocabularies/languages/_new")
    assert response.status_code == 200
    page_text = response.text
    assert "vocabularyProps" in page_text
    assert "vocabularyType" in page_text

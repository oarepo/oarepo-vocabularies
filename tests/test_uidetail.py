# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

import pytest
from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AuthenticatedUser
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType

from oarepo_vocabularies.services.config import VocabulariesConfig

if TYPE_CHECKING:
    from invenio_records_permissions.generators import Generator as InvenioGenerator


def remove_ws(x):
    return re.sub(r"\s+", "", x)


def test_uidetail(
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
    detail_page = logged_in_client.get("/vocabularies/languages/fr")
    assert detail_page.status_code == 200


def test_vocabulary_content_negotiation_redirects_for_api_accept_header(
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
    resp = logged_in_client.get(
        "/vocabularies/languages/eng",
        headers={"Accept": "application/json"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/api/vocabularies/languages/eng" in resp.location


@pytest.mark.parametrize(
    ("export_format", "mimetype"),
    [
        ("json", "application/json"),
        ("jsonld", "application/ld+json"),
        ("turtle", "text/turtle"),
        ("ntriples", "application/n-triples"),
        ("rdfxml", "application/rdf+xml"),
    ],
)
def test_record_export(
    export_format,
    mimetype,
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
    detail_page = logged_in_client.get("/vocabularies/languages/fr")
    assert f"/vocabularies/languages/fr/export/{export_format}" in detail_page.text

    resp = logged_in_client.get(f"/vocabularies/languages/fr/export/{export_format}")
    assert resp.status_code == 200
    assert resp.mimetype == mimetype
    assert resp.headers["Content-Disposition"].startswith('attachment; filename="languages-fr.')
    # the item IRI / self link is in every serialization
    assert "/vocabularies/languages/fr" in resp.text


def test_record_export_unknown_format(
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
    assert logged_in_client.get("/vocabularies/languages/fr/export/unknown").status_code == 404


@pytest.fixture
def code_item(db, service, identity):
    """Item of a vocabulary type with a colon in its name, like NMA's "code:programmingLanguages"."""
    VocabularyType.create(id="code:test", pid_type="cdt")
    db.session.commit()
    item = service.create(
        identity,
        {
            "id": "py",
            "type": "code:test",
            "title": {"en": "Python"},
            "description": {"en": "A programming language."},
            "mappings": [
                {
                    "relation": "exactMatch",
                    "scheme": "https://example.org/",
                    "identifier": "https://example.org/python",
                }
            ],
        },
    )
    Vocabulary.index.refresh()
    return item


def test_detail_of_type_with_colon(
    vocabularies_ui_resource,
    logged_in_client,
    fake_manifest,
    app,
    clear_vocabulary_permissions,
    db,
    cache,
    search_clear,
    vocab_cf,
    code_item,
):
    resp = logged_in_client.get("/vocabularies/code:test/py")
    assert resp.status_code == 200
    assert "A programming language." in resp.text
    assert 'id="mappings"' in resp.text
    assert "Exact match" in resp.text
    assert 'href="https://example.org/python"' in resp.text
    assert 'id="upload-info"' in resp.text
    assert 'id="recordExportDownload"' in resp.text
    # a regular user cannot update the item, so there is no Edit button
    assert 'id="record-manage-menu"' not in resp.text


class UpdatePermissionPolicy(RecordPermissionPolicy):
    """Policy that allows updating to authenticated user."""

    can_update: ClassVar[list[InvenioGenerator]] = [AuthenticatedUser()]


def test_detail_manage_menu_for_editor(
    monkeypatch,
    vocabularies_ui_resource,
    logged_in_client,
    fake_manifest,
    app,
    clear_vocabulary_permissions,
    db,
    cache,
    search_clear,
    vocab_cf,
    code_item,
):
    monkeypatch.setitem(app.config, "VOCABULARIES_PERMISSIONS_POLICY", UpdatePermissionPolicy)
    # the policy class was already cached when code_item was created
    monkeypatch.delattr(VocabulariesConfig.permission_policy_cls, "current_permission_policy_class", raising=False)
    resp = logged_in_client.get("/vocabularies/code:test/py")
    assert resp.status_code == 200
    assert 'id="record-manage-menu"' in resp.text
    assert "/vocabularies/code:test/py/edit" in resp.text

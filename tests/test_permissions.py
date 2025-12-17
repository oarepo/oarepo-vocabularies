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
from invenio_pidstore.errors import PIDDeletedError
from invenio_records_resources.services.errors import (
    PermissionDeniedError,
    RecordPermissionDeniedError,
)
from invenio_vocabularies.proxies import current_service as vocab_service

from oarepo_vocabularies.records.api import Vocabulary

from .conftest import (
    AuthenticatedUserPolicyLanguages,
    EveryonePermissionPolicyLanguages,
    EveryonePermissionPolicyLanguagesAndCountries,
    EveryonePermissionPolicyLanguagesNonDangerousOperation,
)


def test_permissions_create_only_languages(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    identity_simple,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = EveryonePermissionPolicyLanguages

    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"

    lang_object2 = vocab_service.create(
        identity_simple,
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in American"},
        },
    )
    assert lang_object2.data["custom_fields"]["blah"] == "Hello in American"

    # try on different vocabulary type
    with pytest.raises(PermissionDeniedError):
        vocab_service.create(
            identity_simple,
            {
                "id": "cze",
                "title": {"en": "Czechia", "da": "Czech"},
                "type": "countries",
            },
        )


def test_permissions_create_read_update_delete_only_languages(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    identity_simple,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = EveryonePermissionPolicyLanguages

    lang_object = vocab_service.create(
        identity_simple,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"

    lang_object2 = vocab_service.read(identity_simple, (lang_type.id, lang_object.id))
    assert lang_object2.data["custom_fields"]["blah"] == "Hello"
    assert lang_object2.id == lang_object.id

    lang_object3 = vocab_service.update(
        identity_simple,
        (lang_type.id, lang_object.id),
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello2"},
        },
    )

    assert lang_object3.id == lang_object.id
    assert lang_object3.data["custom_fields"]["blah"] == "Hello2"

    deleted = vocab_service.delete(identity_simple, (lang_type.id, lang_object.id))
    assert deleted
    with pytest.raises(PIDDeletedError):
        vocab_service.read(identity_simple, (lang_type.id, lang_object.id))


def test_permissions_create_read_only_languages_authenticated_user(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    identity_simple,
    authenticated_identity,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = AuthenticatedUserPolicyLanguages

    lang_object = vocab_service.create(
        authenticated_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"
    with pytest.raises(RecordPermissionDeniedError):
        vocab_service.read(identity_simple, (lang_type.id, lang_object.id))

    with pytest.raises(RecordPermissionDeniedError):
        vocab_service.read(system_identity, (lang_type.id, lang_object.id))


def test_permissions_update_only_languages_non_dangerous_operation(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = EveryonePermissionPolicyLanguagesNonDangerousOperation

    child_object = vocab_service.create(
        system_identity,
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in American"},
        },
    )

    _ = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert child_object.data["custom_fields"]["blah"] == "Hello in American"

    # changing custom fields is non-dangerous
    child_object_updated = vocab_service.update(
        system_identity,
        (lang_type.id, child_object.id),
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in American updated"},
        },
    )
    assert child_object_updated.data["custom_fields"]["blah"] == "Hello in American updated"

    # changing parent is a dangerous operation
    with pytest.raises(PermissionDeniedError):
        vocab_service.update(
            system_identity,
            (lang_type.id, child_object.id),
            {
                "id": "eng.US",
                "title": {"en": "English", "da": "Engelsk"},
                "type": "languages",
                "custom_fields": {"blah": "Hello2"},
                "hierarchy": {"parent": "eng"},
            },
        )

    # but can create language with a parent directly
    child_object_with_parent = vocab_service.create(
        system_identity,
        {
            "id": "eng.UK",
            "title": {"en": "English (UK)", "da": "Engelsk (UK)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in UK"},
            "hierarchy": {"parent": "eng"},
        },
    )
    assert child_object_with_parent.data["custom_fields"]["blah"] == "Hello in UK"

    # changing id is a very dangerous operation
    with pytest.raises(PermissionDeniedError):
        vocab_service.update(
            system_identity,
            (lang_type.id, child_object.id),
            {
                "id": "eng.UK",
                "title": {"en": "English", "da": "Engelsk"},
                "type": "languages",
                "custom_fields": {"blah": "Hello2"},
            },
        )


def test_permissions_search_only_languages(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    identity_simple,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = EveryonePermissionPolicyLanguages

    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"

    lang_object2 = vocab_service.create(
        identity_simple,
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in American"},
        },
    )
    assert lang_object2.data["custom_fields"]["blah"] == "Hello in American"

    Vocabulary.index.refresh()

    results = list(vocab_service.search(system_identity, {}, type=lang_type.id).hits)
    results2 = list(vocab_service.search(identity_simple, {}, type=lang_type.id).hits)
    assert len(results) == len(results2) == 2

    with pytest.raises(PermissionDeniedError):
        vocab_service.search(system_identity, {}, type=countries_type.id)

    with pytest.raises(PermissionDeniedError):
        vocab_service.search(identity_simple, {}, type=countries_type.id)


def test_permissions_create_languages_and_countries(
    app,
    db,
    cache,
    lang_type,
    countries_type,
    vocab_cf,
    search_clear,
    identity_simple,
    clear_vocabulary_permissions,
):
    app.config["VOCABULARIES_PERMISSIONS_POLICY"] = EveryonePermissionPolicyLanguagesAndCountries

    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello"},
        },
    )

    assert lang_object.data["custom_fields"]["blah"] == "Hello"

    lang_object2 = vocab_service.create(
        identity_simple,
        {
            "id": "eng.US",
            "title": {"en": "English (US)", "da": "Engelsk (US)"},
            "type": "languages",
            "custom_fields": {"blah": "Hello in American"},
        },
    )
    assert lang_object2.data["custom_fields"]["blah"] == "Hello in American"

    country_object = vocab_service.create(
        identity_simple,
        {
            "id": "cze",
            "title": {"en": "Czechia", "da": "Czech"},
            "type": "countries",
            "custom_fields": {"blah": "Czechia in English"},
        },
    )

    country_object = vocab_service.create(
        system_identity,
        {
            "id": "svk",
            "title": {"en": "Slovakia", "da": "Slovensko"},
            "type": "countries",
            "custom_fields": {"blah": "Slovakia in English"},
        },
    )
    assert country_object.data["custom_fields"]["blah"] == "Slovakia in English"

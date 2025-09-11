#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import pytest
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDeletedError
from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_vocabularies.records.api import Vocabulary


def test_services_create(app, db, cache, lang_type, vocab_cf, search_clear):
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


def test_services_update(app, db, cache, lang_type, vocab_cf, search_clear):
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

    lang_object2 = vocab_service.update(
        system_identity,
        (lang_type.id, lang_object.id),
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "custom_fields": {"blah": "Hello2"},
        },
    )

    assert lang_object2.id == lang_object.id
    assert lang_object2.data["custom_fields"]["blah"] == "Hello2"


def test_services_read(app, db, cache, lang_type, vocab_cf, search_clear):
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

    lang_object2 = vocab_service.read(system_identity, (lang_type.id, lang_object.id))

    assert lang_object2 is not None
    assert lang_object2.id == "eng"
    assert lang_object2.data["custom_fields"]["blah"] == "Hello"


def test_services_delete(app, db, cache, lang_type, vocab_cf, search_clear):
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

    vocab_service.delete(system_identity, (lang_type.id, lang_object.id))
    with pytest.raises(PIDDeletedError):
        vocab_service.read(system_identity, (lang_type.id, lang_object.id))


def test_services_read_all(app, db, cache, lang_type, vocab_cf, search_clear):
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

    Vocabulary.index.refresh()

    results = vocab_service.read_all(system_identity, fields=["id"], type=lang_type.id, cache=False)

    assert results.total == 1
    assert next(iter(results.hits))["id"] == "eng"


def test_services_read_many(app, db, cache, lang_type, vocab_cf, search_clear):
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

    Vocabulary.index.refresh()

    results = vocab_service.read_many(system_identity, type=lang_type.id, ids=["eng"])

    assert results.total == 1
    assert next(iter(results.hits))["id"] == "eng"


def test_services_exists(app, db, cache, lang_type, vocab_cf, search_clear):
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

    Vocabulary.index.refresh()

    assert vocab_service.exists(system_identity, (lang_type.id, lang_object.id))


def test_services_search(app, db, cache, lang_type, vocab_cf, search_clear):
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

    Vocabulary.index.refresh()

    results = vocab_service.search(system_identity, {"q": "eng"}, type=lang_type.id)
    assert results.total == 1
    assert next(iter(results.hits))["id"] == "eng"

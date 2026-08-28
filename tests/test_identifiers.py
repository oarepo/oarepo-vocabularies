#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for vocabulary identifiers and crosswalks.

This test suite covers:
1. Creating vocabularies with identifiers and crosswalks
2. Updating vocabularies with identifiers and crosswalks
3. Reading vocabularies with identifiers and crosswalks
4. Searching vocabularies by identifiers and crosswalks (using query strings)
5. Filtering vocabularies using filter parameters

Filter Parameters:
- identifier: Filter by identifier value
- identifier-scheme: Filter by identifier scheme
- crosswalk: Filter by crosswalk value
- crosswalk-scheme: Filter by crosswalk scheme

Test Data Fixtures:
The test suite uses three main fixtures to reduce repetition:
- vocab_with_identifiers: English, Czech, French with ISO 639-1 and ISO 639-3 identifiers
- vocab_with_crosswalks: English, Czech, French with LOC, BNF, DNB crosswalks
- vocab_with_both: English, Czech, French with both identifiers and crosswalks
"""

from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from marshmallow import ValidationError

from oarepo_vocabularies.records.api import Vocabulary

# Fixtures for test data


@pytest.fixture
def vocab_with_identifiers(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Create vocabularies with identifiers (English, Czech, French).

    Returns:
        list: List of created vocabulary objects.

    """
    vocab_data_list = [
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
                {"identifier": "en", "scheme": "iso639-1"},
            ],
        },
        {
            "id": "ces",
            "title": {"en": "Czech"},
            "type": "languages",
            "identifiers": [
                {"identifier": "ces", "scheme": "iso639-3"},
                {"identifier": "cs", "scheme": "iso639-1"},
            ],
        },
        {
            "id": "fra",
            "title": {"en": "French"},
            "type": "languages",
            "identifiers": [
                {"identifier": "fra", "scheme": "iso639-3"},
                {"identifier": "fr", "scheme": "iso639-1"},
            ],
        },
    ]
    created_vocabs = []
    for vocab_data in vocab_data_list:
        vocab = vocab_service.create(system_identity, vocab_data)
        created_vocabs.append(vocab)
    Vocabulary.index.refresh()
    return created_vocabs


@pytest.fixture
def vocab_with_crosswalks(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Create vocabularies with crosswalks (English, Czech, French).

    Returns:
        list: List of created vocabulary objects.

    """
    vocab_data_list = [
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
                {"identifier": "eng-bnf", "scheme": "bnf"},
            ],
        },
        {
            "id": "ces",
            "title": {"en": "Czech"},
            "type": "languages",
            "crosswalks": [
                {"identifier": "ces-loc", "scheme": "loc"},
                {"identifier": "ces-dnb", "scheme": "dnb"},
            ],
        },
        {
            "id": "fra",
            "title": {"en": "French"},
            "type": "languages",
            "crosswalks": [
                {"identifier": "fra-bnf", "scheme": "bnf"},
            ],
        },
    ]
    created_vocabs = []
    for vocab_data in vocab_data_list:
        vocab = vocab_service.create(system_identity, vocab_data)
        created_vocabs.append(vocab)
    Vocabulary.index.refresh()
    return created_vocabs


@pytest.fixture
def vocab_with_both(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Create vocabularies with both identifiers and crosswalks.

    Returns:
        list: List of created vocabulary objects.

    """
    vocab_data_list = [
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
            ],
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
            ],
        },
        {
            "id": "ces",
            "title": {"en": "Czech"},
            "type": "languages",
            "identifiers": [
                {"identifier": "ces", "scheme": "iso639-3"},
            ],
            "crosswalks": [
                {"identifier": "ces-bnf", "scheme": "bnf"},
            ],
        },
        {
            "id": "fra",
            "title": {"en": "French"},
            "type": "languages",
            "identifiers": [
                {"identifier": "fra", "scheme": "iso639-3"},
            ],
        },
    ]
    created_vocabs = []
    for vocab_data in vocab_data_list:
        vocab = vocab_service.create(system_identity, vocab_data)
        created_vocabs.append(vocab)
    Vocabulary.index.refresh()
    return created_vocabs


def test_create_with_identifiers(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test creating a vocabulary with identifiers."""
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
                {"identifier": "en", "scheme": "iso639-1"},
            ],
        },
    )

    assert "identifiers" in lang_object.data
    assert len(lang_object.data["identifiers"]) == 2

    # Check that identifiers are present
    schemes = {id_obj["scheme"] for id_obj in lang_object.data["identifiers"]}
    assert "iso639-3" in schemes
    assert "iso639-1" in schemes

    identifiers = {id_obj["identifier"] for id_obj in lang_object.data["identifiers"]}
    assert "eng" in identifiers
    assert "en" in identifiers


def test_create_with_crosswalks(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test creating a vocabulary with crosswalks."""
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
                {"identifier": "eng-bnf", "scheme": "bnf"},
            ],
        },
    )

    assert "crosswalks" in lang_object.data
    assert len(lang_object.data["crosswalks"]) == 2

    # Check that crosswalks are present
    schemes = {cw["scheme"] for cw in lang_object.data["crosswalks"]}
    assert "loc" in schemes
    assert "bnf" in schemes

    identifiers = {cw["identifier"] for cw in lang_object.data["crosswalks"]}
    assert "eng-loc" in identifiers
    assert "eng-bnf" in identifiers


def test_create_with_identifiers_and_crosswalks(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    """Test creating a vocabulary with both identifiers and crosswalks."""
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
                {"identifier": "en", "scheme": "iso639-1"},
            ],
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
                {"identifier": "eng-bnf", "scheme": "bnf"},
            ],
        },
    )

    assert len(lang_object.data["identifiers"]) == 2
    assert len(lang_object.data["crosswalks"]) == 2


def test_create_with_duplicate_identifier_schemes(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    """Test that creating with duplicate identifier schemes (same scheme) raises validation error."""
    # IdentifierSet should not allow multiple identifiers with the same scheme
    with pytest.raises(ValidationError) as exc_info:
        vocab_service.create(
            system_identity,
            {
                "id": "eng",
                "title": {"en": "English"},
                "type": "languages",
                "identifiers": [
                    {"identifier": "eng", "scheme": "iso639-3"},
                    {"identifier": "english", "scheme": "iso639-3"},  # duplicate scheme
                ],
            },
        )

    assert "identifiers" in str(exc_info.value)


def test_create_with_duplicate_crosswalk_values(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    """Test that creating with duplicate crosswalk entries raises validation error."""
    # IdentifierValueSet should not allow exact duplicate entries (same scheme + identifier)
    with pytest.raises(ValidationError) as exc_info:
        vocab_service.create(
            system_identity,
            {
                "id": "eng",
                "title": {"en": "English"},
                "type": "languages",
                "crosswalks": [
                    {"identifier": "eng-loc", "scheme": "loc"},
                    {"identifier": "eng-loc", "scheme": "loc"},  # exact duplicate
                ],
            },
        )

    assert "crosswalks" in str(exc_info.value)


def test_update_identifiers(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test updating vocabulary identifiers."""
    # Create initial vocabulary
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
            ],
        },
    )

    assert len(lang_object.data["identifiers"]) == 1

    # Update with additional identifier
    lang_object2 = vocab_service.update(
        system_identity,
        (lang_type.id, lang_object.id),
        {
            **lang_object.data,
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
                {"identifier": "en", "scheme": "iso639-1"},
            ],
        },
    )

    assert lang_object2.id == lang_object.id
    assert len(lang_object2.data["identifiers"]) == 2

    schemes = {id_obj["scheme"] for id_obj in lang_object2.data["identifiers"]}
    assert "iso639-3" in schemes
    assert "iso639-1" in schemes


def test_update_crosswalks(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test updating vocabulary crosswalks."""
    # Create initial vocabulary
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
            ],
        },
    )

    assert len(lang_object.data["crosswalks"]) == 1

    # Update with additional crosswalk
    lang_object2 = vocab_service.update(
        system_identity,
        (lang_type.id, lang_object.id),
        {
            **lang_object.data,
            "crosswalks": [
                {"identifier": "eng-loc", "scheme": "loc"},
                {"identifier": "eng-bnf", "scheme": "bnf"},
            ],
        },
    )

    assert lang_object2.id == lang_object.id
    assert len(lang_object2.data["crosswalks"]) == 2


def test_update_remove_identifiers(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test removing identifiers via update."""
    # Create with identifiers
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
                {"identifier": "en", "scheme": "iso639-1"},
            ],
        },
    )

    assert len(lang_object.data["identifiers"]) == 2

    # Update to remove one identifier
    lang_object2 = vocab_service.update(
        system_identity,
        (lang_type.id, lang_object.id),
        {
            **lang_object.data,
            "identifiers": [
                {"identifier": "en", "scheme": "iso639-1"},
            ],
        },
    )

    assert lang_object2.id == lang_object.id
    assert len(lang_object2.data["identifiers"]) == 1
    assert lang_object2.data["identifiers"][0]["scheme"] == "iso639-1"


def test_read_vocabulary_with_identifiers(vocab_with_identifiers, lang_type):
    """Test reading a vocabulary with identifiers."""
    # Use the first vocabulary from the fixture (eng)
    lang_object = vocab_with_identifiers[0]

    # Read back the vocabulary
    lang_object2 = vocab_service.read(system_identity, (lang_type.id, lang_object.id))

    assert lang_object2.id == "eng"
    assert len(lang_object2.data["identifiers"]) == 2

    schemes = {id_obj["scheme"] for id_obj in lang_object2.data["identifiers"]}
    assert "iso639-3" in schemes
    assert "iso639-1" in schemes


def test_read_vocabulary_with_crosswalks(vocab_with_crosswalks, lang_type):
    """Test reading a vocabulary with crosswalks."""
    # Use the first vocabulary from the fixture (eng)
    lang_object = vocab_with_crosswalks[0]

    # Read back the vocabulary
    lang_object2 = vocab_service.read(system_identity, (lang_type.id, lang_object.id))

    assert lang_object2.id == "eng"
    assert len(lang_object2.data["crosswalks"]) == 2

    schemes = {cw["scheme"] for cw in lang_object2.data["crosswalks"]}
    assert "loc" in schemes
    assert "bnf" in schemes


def test_search_by_identifier_scheme(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_identifiers
):
    """Test searching vocabularies by identifier scheme."""
    # Search for vocabularies with iso639-3 scheme
    results = vocab_service.search(system_identity, {"q": "identifiers.scheme:iso639-3"}, type=lang_type.id)

    assert results.total == 3

    # Search for vocabularies with iso639-1 scheme
    results = vocab_service.search(system_identity, {"q": "identifiers.scheme:iso639-1"}, type=lang_type.id)

    assert results.total == 3


def test_search_by_identifier_value(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_identifiers
):
    """Test searching vocabularies by identifier value."""
    # Search by specific identifier
    results = vocab_service.search(system_identity, {"q": "identifiers.identifier:eng"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"

    # Search by different identifier
    results = vocab_service.search(system_identity, {"q": "identifiers.identifier:en"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_search_by_crosswalk_scheme(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_crosswalks
):
    """Test searching vocabularies by crosswalk scheme."""
    # Search for vocabularies with loc crosswalks
    results = vocab_service.search(system_identity, {"q": "crosswalks.scheme:loc"}, type=lang_type.id)

    assert results.total == 2

    # Search for vocabularies with bnf crosswalks
    results = vocab_service.search(system_identity, {"q": "crosswalks.scheme:bnf"}, type=lang_type.id)

    assert results.total == 2


def test_search_by_crosswalk_value(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_crosswalks
):
    """Test searching vocabularies by crosswalk identifier value."""
    # Search by specific crosswalk identifier
    results = vocab_service.search(system_identity, {"q": "crosswalks.identifier:eng-loc"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_search_combined_identifiers_and_crosswalks(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_both
):
    """Test searching with both identifiers and crosswalks."""
    # Search for vocabularies with both identifiers and crosswalks
    results = vocab_service.search(
        system_identity, {"q": "identifiers.scheme:iso639-3 AND crosswalks.scheme:loc"}, type=lang_type.id
    )

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_read_all_with_identifiers(vocab_with_identifiers, lang_type):
    """Test read_all returns vocabularies with identifiers."""
    # Fixture already created 3 vocabularies (eng, ces, fra)
    results = vocab_service.read_all(system_identity, fields=[], type=lang_type.id, cache=False)
    assert results.total == 3

    # Check that all have identifiers
    for hit in results.hits:
        assert "identifiers" in hit
        assert len(hit["identifiers"]) == 2  # All have 2 identifiers (iso639-3 and iso639-1)


def test_read_many_with_identifiers(vocab_with_identifiers, lang_type):
    """Test read_many returns vocabularies with identifiers."""
    # Fixture already created 3 vocabularies (eng, ces, fra)
    results = vocab_service.read_many(system_identity, type=lang_type.id, ids=["eng", "ces"])

    assert results.total == 2
    for hit in results.hits:
        assert "identifiers" in hit
        assert len(hit["identifiers"]) == 2  # Both have 2 identifiers (iso639-3 and iso639-1)


def test_empty_identifiers_and_crosswalks(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    """Test creating vocabulary with empty identifiers and crosswalks."""
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [],
            "crosswalks": [],
        },
    )

    # Empty lists should be allowed
    assert "identifiers" in lang_object.data
    assert len(lang_object.data["identifiers"]) == 0
    assert "crosswalks" in lang_object.data
    assert len(lang_object.data["crosswalks"]) == 0


def test_omitted_identifiers_and_crosswalks(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    """Test creating vocabulary without specifying identifiers and crosswalks."""
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
        },
    )

    # Should be created successfully without identifiers/crosswalks
    assert lang_object.id == "eng"
    # They might be empty lists or not present
    assert lang_object.data.get("identifiers", []) == []
    assert lang_object.data.get("crosswalks", []) == []


# Tests for filter parameters


def test_filter_by_identifier_param(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_identifiers
):
    """Test filtering vocabularies using the 'identifier' parameter."""
    # Filter by specific identifier value
    results = vocab_service.search(system_identity, params={"identifier": "eng"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"

    # Filter by another identifier
    results = vocab_service.search(system_identity, params={"identifier": "cs"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "ces"

    # Filter by multiple identifiers (should work with list)
    results = vocab_service.search(system_identity, params={"identifier": ["en", "fr"]}, type=lang_type.id)

    assert results.total == 2
    ids = {hit["id"] for hit in results.hits}
    assert "eng" in ids
    assert "fra" in ids


def test_filter_by_identifier_scheme_param(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_identifiers
):
    """Test filtering vocabularies using the 'identifier-scheme' parameter."""
    # Filter by scheme
    results = vocab_service.search(system_identity, params={"identifier-scheme": "iso639-1"}, type=lang_type.id)

    assert results.total == 3

    # Filter by different scheme
    results = vocab_service.search(system_identity, params={"identifier-scheme": "iso639-3"}, type=lang_type.id)

    assert results.total == 3


def test_filter_by_crosswalk_param(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_crosswalks
):
    """Test filtering vocabularies using the 'crosswalk' parameter."""
    # Filter by specific crosswalk value
    results = vocab_service.search(system_identity, params={"crosswalk": "eng-loc"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"

    # Filter by another crosswalk
    results = vocab_service.search(system_identity, params={"crosswalk": "ces-dnb"}, type=lang_type.id)

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "ces"

    # Filter by multiple crosswalks
    results = vocab_service.search(system_identity, params={"crosswalk": ["eng-bnf", "fra-bnf"]}, type=lang_type.id)

    assert results.total == 2
    ids = {hit["id"] for hit in results.hits}
    assert "eng" in ids
    assert "fra" in ids


def test_filter_by_crosswalk_scheme_param(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_crosswalks
):
    """Test filtering vocabularies using the 'crosswalk-scheme' parameter."""
    # Filter by crosswalk scheme
    results = vocab_service.search(system_identity, params={"crosswalk-scheme": "loc"}, type=lang_type.id)

    assert results.total == 2
    ids = {hit["id"] for hit in results.hits}
    assert "eng" in ids
    assert "ces" in ids

    # Filter by different scheme
    results = vocab_service.search(system_identity, params={"crosswalk-scheme": "bnf"}, type=lang_type.id)

    assert results.total == 2
    ids = {hit["id"] for hit in results.hits}
    assert "eng" in ids
    assert "fra" in ids


def test_filter_combined_identifier_and_scheme(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_identifiers
):
    """Test filtering with both identifier and scheme parameters."""
    # Filter by both identifier and scheme
    results = vocab_service.search(
        system_identity,
        params={
            "identifier": "eng",
            "identifier-scheme": "iso639-3",
        },
        type=lang_type.id,
    )

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_filter_combined_crosswalk_and_scheme(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_crosswalks
):
    """Test filtering with both crosswalk and scheme parameters."""
    # Filter by both crosswalk and scheme
    results = vocab_service.search(
        system_identity,
        params={
            "crosswalk": "eng-loc",
            "crosswalk-scheme": "loc",
        },
        type=lang_type.id,
    )

    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_filter_mixed_identifiers_and_crosswalks(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, vocab_with_both
):
    """Test filtering with both identifier and crosswalk parameters."""
    # Filter by identifier scheme AND crosswalk scheme
    results = vocab_service.search(
        system_identity,
        params={
            "identifier-scheme": "iso639-3",
            "crosswalk-scheme": "loc",
        },
        type=lang_type.id,
    )

    # Should only return eng (has both iso639-3 identifier and loc crosswalk)
    assert results.total == 1
    first_item = next(iter(results.hits))
    assert first_item["id"] == "eng"


def test_filter_no_results(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    """Test filtering with parameters that match no vocabularies."""
    # Create a vocabulary
    vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "identifiers": [
                {"identifier": "eng", "scheme": "iso639-3"},
            ],
        },
    )

    Vocabulary.index.refresh()

    # Filter by non-existent identifier
    results = vocab_service.search(system_identity, params={"identifier": "nonexistent"}, type=lang_type.id)

    assert results.total == 0

    # Filter by non-existent scheme
    results = vocab_service.search(
        system_identity, params={"identifier-scheme": "nonexistent-scheme"}, type=lang_type.id
    )

    assert results.total == 0

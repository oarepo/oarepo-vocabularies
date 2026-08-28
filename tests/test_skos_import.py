#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests that known SKOS mapping schemes are converted to RDM-compatible props on import."""

from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from oarepo_runtime.typing import record_from_result

SKOS_MAPPING_CASES = [
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/dateType/",
        "https://schema.datacite.org/meta/kernel-4/dateType/Issued",
        {"datacite": "Issued"},
        id="datacite-dateType",
    ),
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/descriptionType/",
        "https://schema.datacite.org/meta/kernel-4/descriptionType/Abstract",
        {"datacite": "Abstract"},
        id="datacite-descriptionType",
    ),
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/relationType/",
        "https://schema.datacite.org/meta/kernel-4/relationType/Cites",
        {"datacite": "Cites"},
        id="datacite-relationType",
    ),
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/contributorType/",
        "https://schema.datacite.org/meta/kernel-4/contributorType/DataCollector",
        {"datacite": "DataCollector"},
        id="datacite-contributorType",
    ),
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/titleType/",
        "https://schema.datacite.org/meta/kernel-4/titleType/AlternativeTitle",
        {"datacite": "AlternativeTitle"},
        id="datacite-titleType",
    ),
    pytest.param(
        "https://schema.datacite.org/meta/kernel-4/resourceType/",
        "https://schema.datacite.org/meta/kernel-4/resourceType/Dataset",
        {"datacite_general": "Dataset", "type": "Dataset"},
        id="datacite-resourceType",
    ),
    pytest.param(
        "https://guidelines.openaire.eu/en/latest/data/field_resourcetype.html#",
        "https://guidelines.openaire.eu/en/latest/data/field_resourcetype.html#literature",
        {"openaire_type": "literature"},
        id="openaire-resourceType",
    ),
    pytest.param(
        "info:eu-repo/semantics/",
        "info:eu-repo/semantics/openAccess",
        {"eurepo": "openAccess"},
        id="eu-repo-semantics",
    ),
    pytest.param(
        "https://schema.org/",
        "https://schema.org/Book",
        {"schema.org": "Book"},
        id="schema.org",
    ),
]


@pytest.mark.parametrize(("scheme", "identifier", "expected_props"), SKOS_MAPPING_CASES)
def test_skos_mapping_rdm_props(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, scheme, identifier, expected_props
):
    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "mappings": [
                {"identifier": identifier, "scheme": scheme, "relation": "exactMatch"},
            ],
        },
    )

    assert record_from_result(result)["props"] == expected_props


def test_skos_mapping_unknown_scheme_not_converted(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "mappings": [
                {"identifier": "12345", "scheme": "myscheme", "relation": "exactMatch"},
            ],
        },
    )

    assert "props" not in record_from_result(result)


RELATION_EXPORT_ELIGIBILITY_CASES = [
    pytest.param("exactMatch", True, id="exactMatch"),
    pytest.param("broadMatch", True, id="broadMatch"),
    pytest.param("narrowMatch", False, id="narrowMatch"),
    pytest.param("closeMatch", False, id="closeMatch"),
    pytest.param("relatedMatch", False, id="relatedMatch"),
]


@pytest.mark.parametrize(("relation", "expect_props"), RELATION_EXPORT_ELIGIBILITY_CASES)
def test_skos_mapping_relation_export_eligibility(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, relation, expect_props
):
    """Only exactMatch/broadMatch relations are usable for export, so only those produce RDM props."""
    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
            "mappings": [
                {
                    "identifier": "https://schema.org/Book",
                    "scheme": "https://schema.org/",
                    "relation": relation,
                },
            ],
        },
    )

    record = record_from_result(result)
    if expect_props:
        assert record["props"] == {"schema.org": "Book"}
    else:
        assert "props" not in record

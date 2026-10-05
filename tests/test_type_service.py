# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

from oarepo_vocabularies.proxies import current_type_service as vocabulary_type_service


def test_counts(
    app,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
    clear_vocabulary_permissions,
):
    search_result = vocabulary_type_service.search(identity)
    results = search_result.to_dict()

    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0

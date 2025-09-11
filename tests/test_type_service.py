#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from oarepo_vocabularies.proxies import current_type_service as vocabulary_type_service


def test_counts(
    app,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
):
    search_result = vocabulary_type_service.search(identity)
    results = search_result.to_dict()

    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0

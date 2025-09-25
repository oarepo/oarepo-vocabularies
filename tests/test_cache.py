#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import time

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.mark.skip(reason="We want to remove cache, need to load fixtures too")
def test_cache_fast(app, db, vocab_cf, reset_babel, cache_clear, search_clear):
    # load_fixtures here...
    Vocabulary.index.refresh()

    # import cache here...
    cache = {}  # placeholder
    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t1_cs = time.time()
        data = cache.get(["languages"])
        t1_cs = time.time() - t1_cs
        assert len(data) == 1

    reset_babel()

    count_fetched = cache.count_fetched
    count_prefetched = cache.count_prefetched

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t2_cs = time.time()
        data = cache.get(["languages"])
        t2_cs = time.time() - t2_cs
        assert len(data) == 1

    reset_babel()

    # check that no more cache fetching was performed
    assert cache.count_fetched == count_fetched
    assert cache.count_prefetched == count_prefetched


@pytest.mark.skip(reason="We want to remove cache, need to load fixtures too")
def test_cache(app, db, vocab_cf, reset_babel, cache_clear, search_clear):
    # load_fixtures here...
    Vocabulary.index.refresh()

    # import cache here...
    cache = {}  # placeholder

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t1_cs = time.time()
        data = cache.get(["institutions", "languages"])
        t1_cs = time.time() - t1_cs
        assert len(data) == 2

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        t1_en = time.time()
        data = cache.get(["institutions", "languages"])
        t1_en = time.time() - t1_en
        assert len(data) == 2

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t2_cs = time.time()
        data = cache.get(["institutions", "languages"])
        t2_cs = time.time() - t2_cs
        assert len(data) == 2

    assert t2_cs < t1_cs / 2


@pytest.mark.skip(reason="We want to remove cache, need to load fixtures too")
def test_cache_resolve(app, db, vocab_cf, reset_babel, cache_clear, search_clear):
    # load_fixtures here...
    Vocabulary.index.refresh()

    # import cache here...
    cache = {}  # placeholder

    ids = [
        ("institutions", "amu-hamu"),
        ("institutions", "amu-hamu-katedra-dirigovani"),
        ("institutions", "amu-hamu-katedra-zpevu-a-operni-rezie"),
        ("institutions", "amu-hamu-katedra-skladby"),
        ("institutions", "amu-hamu-katedra-klavesovych-nastroju"),
        ("institutions", "amu-hamu-katedra-strunnych-nastroju"),
        ("institutions", "amu-hamu-katedra-dechovych-nastroju"),
        ("institutions", "amu-hamu-katedra-tance"),
        ("institutions", "amu-hamu-oddeleni-hudebne-teoretickych-disciplin"),
        ("institutions", "amu-hamu-katedra-nonverbalniho-divadla"),
        ("institutions", "amu-hamu-oddeleni-klavirni-spoluprace"),
        ("institutions", "amu-hamu-katedra-zvukove-tvorby"),
        ("institutions", "amu-hamu-katedra-bicich-nastroju"),
        ("institutions", "amu-hamu-oddeleni-komorni-hry"),
        ("institutions", "amu-hamu-katedra-jazzove-hudby"),
        ("institutions", "amu-hamu-katedra-hudebni-produkce"),
        ("institutions", "amu-hamu-katedra-hudebni-teorie"),
        ("institutions", "amu-hamu-oddeleni-historicky-poucene-interpretace"),
        ("institutions", "amu-hamu-oddeleni-soudobe-hudby"),
        ("languages", "cs"),
        ("languages", "en"),
        ("languages", "de"),
    ]

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        time_cs_1 = time.time()
        data = cache.resolve(ids)
        time_cs_1 = time.time() - time_cs_1
        assert len(data) == len(ids)

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        time_en_1 = time.time()
        data = cache.resolve(ids)
        time_en_1 = time.time() - time_en_1
        assert len(data) == len(ids)

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        time_cs_2 = time.time()
        data = cache.resolve(ids)
        time_cs_2 = time.time() - time_cs_2
        assert len(data) == len(ids)


@pytest.mark.skip(reason="We want to remove cache, need to load fixtures too")
def test_cache_resolve_fast(app, db, vocab_cf, reset_babel, cache_clear, search_clear):
    # load_fixtures here...
    Vocabulary.index.refresh()

    assert len(list(vocabulary_service.scan(system_identity, type="languages"))) == 2

    # import cache here...
    cache = {}  # placeholder

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        time_cs_1 = time.time()
        data = cache.resolve([("languages", "en")])
        time_cs_1 = time.time() - time_cs_1
        assert len(data) == 1

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        time_en_1 = time.time()
        data = cache.resolve([("languages", "en")])
        time_en_1 = time.time() - time_en_1
        assert len(data) == 1

    count_fetched = cache.count_fetched
    count_prefetched = cache.count_prefetched

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        time_cs_2 = time.time()
        data = cache.resolve([("languages", "en")])
        time_cs_2 = time.time() - time_cs_2
        assert len(data) == 1

    assert count_fetched == cache.count_fetched
    assert count_prefetched == cache.count_prefetched

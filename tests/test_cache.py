import time
from pathlib import Path

from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures

from oarepo_vocabularies.ui.resources.cache import VocabularyCache

def test_cache_fast(app, db, vocab_cf, reset_babel, cache_clear):
    load_fixtures(Path(__file__).parent / "data", callback=FixturesCallback())
    Vocabulary.index.refresh()

    cache = VocabularyCache()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t1_cs = time.time()
        data = cache.get(['languages'])
        t1_cs = time.time() - t1_cs
        assert len(data) == 1

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t2_cs = time.time()
        data = cache.get(['languages'])
        t2_cs = time.time() - t2_cs
        assert len(data) == 1

    reset_babel()

    print(f"Cache time: {t1_cs=} {t2_cs=}")
    assert t2_cs < t1_cs / 2


def test_cache(app, db, vocab_cf, reset_babel, cache_clear):
    load_fixtures(Path(__file__).parent / "complex-data", callback=FixturesCallback())
    Vocabulary.index.refresh()

    cache = VocabularyCache()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t1_cs = time.time()
        data = cache.get(['institutions', 'languages'])
        t1_cs = time.time() - t1_cs
        assert len(data) == 2

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        t1_en = time.time()
        data = cache.get(['institutions', 'languages'])
        t1_en = time.time() - t1_en
        assert len(data) == 2

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        t2_cs = time.time()
        data = cache.get(['institutions', 'languages'])
        t2_cs = time.time() - t2_cs
        assert len(data) == 2

    print(f"Cache time: {t1_cs=} {t1_en=} {t2_cs=}")
    assert t2_cs < t1_cs / 2

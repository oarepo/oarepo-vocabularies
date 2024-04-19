from pathlib import Path

from oarepo_runtime.datastreams import StreamBatch
from oarepo_runtime.datastreams.fixtures import load_fixtures, FixturesCallback

from oarepo_vocabularies.records.api import Vocabulary


def test_serialization_api(app, db, cache, vocab_cf, reset_babel, search_clear, cache_clear, identity, client):
    class CB(FixturesCallback):
        def batch_finished(self, batch: StreamBatch):
            super().batch_finished(batch)
            for b in batch.entries:
                if b.errors:
                    print(b.errors)
                    raise Exception("Fixture load error")


    load_fixtures(
        Path(__file__).parent / "cfdata",
        callback=CB()
    )
    Vocabulary.index.refresh()

    with client.get("/api/vocabularies/languages") as response:
        assert response.status_code == 200
        hits = response.json['hits']['hits']
        assert len(hits) == 2

        assert hits[0]['title']['cs'] == 'Čeština'
        assert hits[0]['props']['alpha3CodeNative'] == 'ces'
        assert hits[0]['relatedURI']['url'] == 'http://cs.com'

        assert hits[1]['title']['en'] == 'English'
        assert hits[1]['props']['alpha3CodeNative'] == 'eng'
        assert hits[1]['relatedURI']['url'] == 'http://en.com'


def test_serialization_api_vnd(app, db, cache, vocab_cf, reset_babel, search_clear, cache_clear, identity, client):
    class CB(FixturesCallback):
        def batch_finished(self, batch: StreamBatch):
            super().batch_finished(batch)
            for b in batch.entries:
                if b.errors:
                    print(b.errors)
                    raise Exception("Fixture load error")


    load_fixtures(
        Path(__file__).parent / "cfdata",
        callback=CB()
    )
    Vocabulary.index.refresh()

    with client.get("/api/vocabularies/languages", headers={'Accept': "application/vnd.inveniordm.v1+json",
                                                            "Accept-Language": "cs"}) as response:
        assert response.status_code == 200
        hits = response.json['hits']['hits']
        assert len(hits) == 2

        assert hits[1]['title'] == 'Čeština'
        assert hits[1]['props']['alpha3CodeNative'] == 'ces'
        assert hits[1]['relatedURI']['url'] == 'http://cs.com'

        assert hits[0]['title'] == 'Angličtina'
        assert hits[0]['props']['alpha3CodeNative'] == 'eng'
        assert hits[0]['relatedURI']['url'] == 'http://en.com'

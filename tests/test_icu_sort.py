from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures


def test_icu_sort(app, db, cache, vocab_cf, reset_babel):
    load_fixtures(Path(__file__).parent / "icudata", callback=FixturesCallback())
    Vocabulary.index.refresh()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        titles = []
        for rec in current_service.search(
            system_identity, params={"sort": "title"}, type="languages"
        ):
            titles.append(rec["title"]["cs"])
        assert titles == ["Angličtina", "Čeština"]

    reset_babel()

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        titles = []
        for rec in current_service.search(
            system_identity, params={"sort": "title"}, type="languages"
        ):
            titles.append(rec["title"]["cs"])
        assert titles == ["Čeština", "Angličtina"]

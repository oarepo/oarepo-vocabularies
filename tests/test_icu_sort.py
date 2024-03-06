from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import load_fixtures, FixturesCallback
from flask import g


def clear_babel_context():
    # for invenio 12
    try:
        from flask_babel import SimpleNamespace
    except ImportError:
        return
    g._flask_babel = SimpleNamespace()

def test_icu_sort(app, db, cache, vocab_cf):
    load_fixtures(Path(__file__).parent / "icudata", callback=FixturesCallback())
    Vocabulary.index.refresh()

    with app.test_request_context(headers=[("Accept-Language", "cs")]):
        titles = []
        for rec in current_service.search(system_identity, params={"sort": "title"}, type="languages"):
            titles.append(rec["title"]['cs'])
        assert titles == ['Angličtina', 'Čeština']

    clear_babel_context()

    with app.test_request_context(headers=[("Accept-Language", "en")]):
        titles = []
        for rec in current_service.search(system_identity, params={"sort": "title"}, type="languages"):
            titles.append(rec["title"]['cs'])
        assert titles == ['Čeština', 'Angličtina']

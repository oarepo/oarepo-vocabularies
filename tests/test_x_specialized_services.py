from pathlib import Path

from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocab_service
from oarepo_runtime.datastreams.fixtures import load_fixtures
from oarepo_runtime.datastreams.types import StatsKeepingDataStreamCallback

from oarepo_vocabularies.services.service import VocabulariesService

vocab_service: VocabulariesService

def test_names_crud(app, db, cache, vocab_cf, search_clear):
    rec = vocab_service.create(
        identity=system_identity,
        data={
            "type": "names",
            "id": "test",
            "given_name": "Mirek",
            "family_name": "Svoboda",
        }
    )

    full_rec = {'id': 'test',
            'links': {'self': 'https://127.0.0.1:5000/api/names/test'},
            'revision_id': 2, 'name': 'Svoboda, Mirek',
            'given_name': 'Mirek', 'family_name': 'Svoboda'}

    assert full_rec.items() <= rec.data.items()

    current_service_registry.get("names").indexer.refresh()

    all_names = list(vocab_service.search(system_identity, type="names").hits)
    assert len(all_names) == 1
    assert full_rec.items() <= all_names[0].items()

    rec = vocab_service.update(
        identity=system_identity,
        id_=("names", "test"),
        data={
            "given_name": "Jana",
            "family_name": "Novotna",
        }
    )

    current_service_registry.get("names").indexer.refresh()

    rec = vocab_service.read(system_identity, ("names", "test"))
    assert {"given_name": "Jana",
            "family_name": "Novotna",}.items() <= rec.data.items()


def test_names_fixtures_load(app, db, cache, vocab_cf, search_clear):
    callback = StatsKeepingDataStreamCallback(log_error_entry=True)
    load_fixtures(Path(__file__).parent / "names-data", callback=callback)
    assert callback.ok_entries_count == 1
    assert callback.failed_entries_count == 0
    assert callback.filtered_entries_count == 0

    names_service = current_service_registry.get("names")
    names_service.indexer.refresh()
    correct = {
        "given_name": "Mirek",
        "family_name": "Svoboda",
    }
    # through vocab service
    assert correct.items() <= vocab_service.read(system_identity, ("names", "test")).data.items()

    # through names service
    assert correct.items() <= names_service.read(system_identity, "test").data.items()


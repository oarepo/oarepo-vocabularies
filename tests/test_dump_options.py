from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records import Record
from invenio_records_resources.records.systemfields import PIDField
from invenio_records_resources.records.systemfields.pid import PIDFieldContext

from oarepo_vocabularies.ui.resources.components.record_ui_resource import (
    RecordVocabularyUIComponent,
)
from tests.simple_model import ModelRecord


def test_dump_options(sample_records, search_clear, identity):
    comp = RecordVocabularyUIComponent(service=None)
    form_config = {}
    rec = ModelRecord({})
    comp.form_config(
        form_config=form_config,
        resource=None,
        record=rec,
        view_args={},
        identity=identity,
    )

    assert form_config == {
        "vocabularies": {
            "authority": {
                "definition": {"authority": "AuthService", "name": {"en": "authority"}},
                "url": "/api/vocabularies/authority",
            },
            "languages": {
                "all": [
                    {"text": "English", "value": "eng"},
                    {"text": "English (US)", "value": "eng.US"},
                    {"text": "English (UK)", "value": "eng.UK"},
                ],
                "definition": {
                    "description": {
                        "cs": "slovnikovy typ ceskeho jazyka.",
                        "en": "czech language vocabulary type.",
                    },
                    "dump_options": True,
                    "name": {"cs": "jazyky", "en": "languages"},
                },
                "featured": [{"text": "English (UK, Scotland)", "value": "eng.UK.S"}],
            },
        }
    }

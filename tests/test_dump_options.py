from invenio_records_resources.services.records.results import RecordItem

from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from tests.simple_model import ModelRecord


def test_dump_options(
    sample_records,
    simple_record_service,
    simple_record_ui_resource,
    search_clear,
    identity,
):
    comp = DepositVocabularyOptionsComponent(resource=simple_record_ui_resource)
    form_config = {}
    rec = ModelRecord({})
    comp.form_config(
        form_config=form_config,
        api_record=RecordItem(
            service=simple_record_service, identity=identity, record=rec
        ),
        view_args={},
        identity=identity,
    )

    assert form_config == {
        "vocabularies": {
            "authority": {
                "definition": {"name": {"en": "authority"}, "authority": "AuthService"},
                "url": "/api/vocabularies/authority",
            },
            "languages": {
                "definition": {
                    "name": {"cs": "jazyky", "en": "languages"},
                    "description": {
                        "cs": "slovnikovy typ ceskeho jazyka.",
                        "en": "czech language vocabulary type.",
                    },
                    "dump_options": True,
                },
                "all": [
                    {
                        "value": "eng",
                        "text": "English",
                        "hierarchy": {"title": ["English"], "ancestors": []},
                        "element_type": "parent",
                        'props': {'akey': 'avalue'},
                    },
                    {
                        "value": "eng.UK.S",
                        "text": "English (UK, Scotland)",
                        "hierarchy": {
                            "title": [
                                "English (UK, Scotland)",
                                "English (UK)",
                                "English",
                            ],
                            "ancestors": ["eng.UK", "eng"],
                        },
                        "element_type": "leaf",
                    },
                    {
                        "value": "eng.UK",
                        "text": "English (UK)",
                        "hierarchy": {
                            "title": ["English (UK)", "English"],
                            "ancestors": ["eng"],
                        },
                        "element_type": "parent",
                    },
                    {
                        "value": "eng.US",
                        "text": "English (US)",
                        "hierarchy": {
                            "title": ["English (US)", "English"],
                            "ancestors": ["eng"],
                        },
                        "element_type": "leaf",
                    },
                ],
                "featured": [
                    {
                        "value": "eng.UK.S",
                        "text": "English (UK, Scotland)",
                        "hierarchy": {
                            "title": [
                                "English (UK, Scotland)",
                                "English (UK)",
                                "English",
                            ],
                            "ancestors": ["eng.UK", "eng"],
                        },
                        "element_type": "leaf",
                    }
                ],
            },
        }
    }

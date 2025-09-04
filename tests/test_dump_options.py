import pytest
from invenio_records_resources.services.records.results import RecordItem

from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from tests.simple_model import ModelRecord


@pytest.mark.skip(
    reason="AttributeError: 'Cfg' object has no attribute 'model_name' in oarepo_ui/resources/records/config.py"
)
def test_dump_options(
    sample_records,
    simple_record_service,
    simple_record_ui_resource,
    search_clear,
    cache_clear,
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
            "creator": {"definition": {}, "url": "/api/vocabularies/creator"},
            "award": {"definition": {}, "url": "/api/vocabularies/award"},
            "ror-authority": {
                "definition": {
                    "authority": "RORProviderV2",
                    "name": {"en": "ROR Authority"},
                },
                "url": "/api/vocabularies/ror-authority",
            },
            "languages": {
                "definition": {
                    "name": {"cs": "jazyky", "en": "languages"},
                    "description": {
                        "cs": "slovnikovy typ ceskeho jazyka.",
                        "en": "czech language vocabulary type.",
                    },
                    "dump_options": True,
                    "custom_fields": ["relatedURI"],
                    "props": {
                        "alpha3CodeNative": {
                            "description": "ISO 639-2 standard 3-letter language code",
                            "icon": None,
                            "label": "Alpha3 code (native)",
                            "multiple": False,
                            "options": [],
                            "placeholder": "eng, ces...",
                        }
                    },
                },
                "all": [
                    {
                        "value": "eng",
                        "text": "English",
                        "hierarchy": {"title": ["English"], "ancestors": []},
                        "element_type": "parent",
                        "props": {"akey": "avalue"},
                        "tags": ["recommended"],
                        "description": "English description",
                        "icon": "file-o",
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
                        "tags": ["featured"],
                        "element_type": "leaf",
                        "icon": "file-o",
                    },
                    {
                        "value": "eng.UK",
                        "text": "English (UK)",
                        "hierarchy": {
                            "title": ["English (UK)", "English"],
                            "ancestors": ["eng"],
                        },
                        "element_type": "parent",
                        "icon": "file-o",
                    },
                    {
                        "value": "eng.US",
                        "text": "English (US)",
                        "hierarchy": {
                            "title": ["English (US)", "English"],
                            "ancestors": ["eng"],
                        },
                        "element_type": "leaf",
                        "icon": "file-o",
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
                        "tags": ["featured"],
                        "element_type": "leaf",
                        "icon": "file-o",
                    }
                ],
            },
        }
    }

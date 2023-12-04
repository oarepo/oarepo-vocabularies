from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from tests.simple_model import ModelRecord, ModelUIResource, ModelUIResourceConfig


def test_dump_options(sample_records, search_clear, identity):
    comp = DepositVocabularyOptionsComponent(service=None, uow=None)
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
                    {
                        "element_type": "parent",
                        "hierarchy": {"ancestors": [], "title": ["English"]},
                        "text": "English",
                        "value": "eng",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {
                            'ancestors': ['eng.UK', 'eng'],
                            "title": [
                                "English (UK, " "Scotland)",
                                "English (UK)",
                                "English",
                            ]
                        },
                        "text": "English (UK, Scotland)",
                        "value": "eng.UK.S",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {'ancestors': ['eng'],"title": ["English (UK)", "English"]},
                        "text": "English (UK)",
                        "value": "eng.UK",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {'ancestors': ['eng'],"title": ["English (US)", "English"]},
                        "text": "English (US)",
                        "value": "eng.US",
                    },
                ],
                "definition": {
                    "description": {
                        "cs": "slovnikovy typ ceskeho jazyka.",
                        "en": "czech " "language " "vocabulary " "type.",
                    },
                    "dump_options": True,
                    "name": {"cs": "jazyky", "en": "languages"},
                },
                "featured": [
                    {
                        "element_type": "leaf",
                        "hierarchy": {
                            'ancestors': ['eng.UK', 'eng'],
                            "title": [
                                "English " "(UK, " "Scotland)",
                                "English " "(UK)",
                                "English",
                            ]
                        },
                        "text": "English (UK, Scotland)",
                        "value": "eng.UK.S",
                    }
                ],
            },
        }
    }


def test_dump_options_with_resource(
    sample_records, search_clear, simple_record_service, identity
):
    comp = DepositVocabularyOptionsComponent(service=None, uow=None)
    form_config = {}
    comp.form_config(
        form_config=form_config,
        resource=ModelUIResource(config=ModelUIResourceConfig()),
        record={},
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
                    {
                        "element_type": "parent",
                        "hierarchy": {"ancestors": [],"title": ["English"]},
                        "text": "English",
                        "value": "eng",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {
                            'ancestors': ['eng.UK', 'eng'],
                            "title": [
                                "English (UK, " "Scotland)",
                                "English (UK)",
                                "English",
                            ]
                        },
                        "text": "English (UK, Scotland)",
                        "value": "eng.UK.S",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {'ancestors': ['eng'],"title": ["English (UK)", "English"]},
                        "text": "English (UK)",
                        "value": "eng.UK",
                    },
                    {
                        "element_type": "leaf",
                        "hierarchy": {'ancestors': ['eng'],"title": ["English (US)", "English"]},
                        "text": "English (US)",
                        "value": "eng.US",
                    },
                ],
                "definition": {
                    "description": {
                        "cs": "slovnikovy " "typ " "ceskeho " "jazyka.",
                        "en": "czech " "language " "vocabulary " "type.",
                    },
                    "dump_options": True,
                    "name": {"cs": "jazyky", "en": "languages"},
                },
                "featured": [
                    {
                        "element_type": "leaf",
                        "hierarchy": {
                            'ancestors': ['eng.UK', 'eng'],
                            "title": [
                                "English " "(UK, " "Scotland)",
                                "English " "(UK)",
                                "English",
                            ]
                        },
                        "text": "English (UK, Scotland)",
                        "value": "eng.UK.S",
                    }
                ],
            },
        }
    }

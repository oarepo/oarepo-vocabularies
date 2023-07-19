import marshmallow as ma
from flask import current_app
from oarepo_ui.resources.config import RecordsUIResourceConfig

from oarepo_vocabularies.ui.resources.components import VocabulariesSearchComponent


class InvenioVocabulariesUIResourceConfig(RecordsUIResourceConfig):
    template_folder = "../templates"
    url_prefix = "/vocabularies/"
    blueprint_name = "oarepo_vocabularies_ui"
    ui_serializer_class = (
        "oarepo_vocabularies.resources.records.ui.VocabularyUIJSONSerializer"
    )
    api_service = "vocabularies"
    layout = "oarepo_vocabularies_ui"

    templates = {
        "detail": {
            "layout": "oarepo_vocabularies_ui/detail.html",
            "blocks": {
                "record_main_content": "oarepo_vocabularies_ui/main.html",
                "record_sidebar": "oarepo_vocabularies_ui/sidebar.html",
                "vocabulary_descendants": "oarepo_vocabularies_ui/descendants.html",
            },
        },
        "search": {"layout": "oarepo_vocabularies_ui/search.html"},
        "create": {"layout": "oarepo_vocabularies_ui/form.html"},
        "edit": {"layout": "oarepo_vocabularies_ui/form.html"},
    }

    routes = {
        "create": "/<vocabulary_type>/_new",
        "edit": "/<vocabulary_type>/<pid_value>/edit",
        "search": "/<vocabulary_type>/",
        "detail": "/<vocabulary_type>/<pid_value>",
        "export": "/<vocabulary_type>/<pid_value>/export/<export_format>",
    }

    components = [VocabulariesSearchComponent]

    request_vocabulary_type_args = {"vocabulary_type": ma.fields.Str()}

    def form_props_config(self, vocabulary_type):
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(
            vocabulary_type, {}
        )

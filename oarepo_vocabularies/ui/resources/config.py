from oarepo_ui.resources.config import RecordsUIResourceConfig
import marshmallow as ma


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
            },
        },
        "search": {"layout": "oarepo_ui/search.html.jinja2"},
    }

    routes = {
        "search": "",
        "detail": "/<vocabulary_type>/<pid_value>",
        "export": "/<vocabulary_type>/<pid_value>/export/<export_format>",
    }

    request_vocabulary_type_args = {"vocabulary_type": ma.fields.Str()}

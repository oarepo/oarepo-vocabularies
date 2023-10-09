from invenio_base.utils import obj_or_import_string
from oarepo_ui.resources import UIResourceConfig


class VocabularyTypeUIResourceConfig(UIResourceConfig):
    url_prefix = "/vocabularies"
    blueprint_name = "vocabulary_type_app"
    ui_serializer_class = (
        "oarepo_vocabularies.resources.ui.VocabularyTypeUIJSONSerializer"
    )
    api_service = "vocabulary_type"
    layout = "vocabulary"

    templates = {
        "list": {
            "layout": "oarepo_vocabularies_ui/VocabulariesList.jinja",
        }
    }

    routes = {"list": "/"}

    @property
    def ui_serializer(self):
        return obj_or_import_string(self.ui_serializer_class)()

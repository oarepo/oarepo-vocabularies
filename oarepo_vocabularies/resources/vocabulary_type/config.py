from flask_resources import ResourceConfig, ResponseHandler

from oarepo_vocabularies.resources.ui import VocabularyTypeUIJSONSerializer


class VocabularyTypeResourceConfig(ResourceConfig):
    blueprint_name = "vocabulary_types"
    url_prefix = "/vocabularies"

    routes = {
        "list": "/",
    }

    @property
    def response_handlers(self):
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                VocabularyTypeUIJSONSerializer()
            ),
            **super().response_handlers,
        }

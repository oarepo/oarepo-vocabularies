from invenio_vocabularies.resources.resource import VocabulariesResourceConfig
import marshmallow as ma


class OARepoVocabulariesResourceConfigBase(VocabulariesResourceConfig):
    routes = {
        **VocabulariesResourceConfig.routes,
        "item": "/<type>/<path:pid_value>",  # pid value might contain hierarchy
        "vocabularies": ""
    }
    request_hierarchy_args = {
        "hierarchy": ma.fields.Str()
    }

import marshmallow as ma
from flask_resources import ResourceConfig
from invenio_records_resources.resources import SearchRequestArgsSchema


class AuthoritativeVocabulariesResourceConfig(ResourceConfig):
    blueprint_name = "authorities"
    url_prefix = "/vocabularies/<type>/authoritative"

    routes = {"list": ""}

    request_view_args = {
        "type": ma.fields.Str(required=True),
    }

    request_search_args = SearchRequestArgsSchema

import marshmallow as ma
from flask_resources import ResourceConfig
from invenio_records_resources.resources import SearchRequestArgsSchema
from invenio_records_resources.services import pagination_links


class AuthoritativeVocabulariesResourceConfig(ResourceConfig):
    blueprint_name = "authorities"
    url_prefix = "/vocabularies/<vocabulary_type>/authoritative"

    routes = {"list": ""}

    request_view_args = {}
    request_vocabulary_type_args = {"vocabulary_type": ma.fields.Str(required=True)}
    request_search_args = SearchRequestArgsSchema

    @property
    def ui_links_search(self):
        return {
            **pagination_links(
                "{+api}{+}/vocabularies/{+vocabulary_type}{+}/authoritative{?args*}"
            ),
        }

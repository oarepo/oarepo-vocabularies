import marshmallow as ma
from invenio_records_resources.resources import RecordResource, RecordResourceConfig


class HierarchicalVocabulariesResourceConfig(RecordResourceConfig):
    """Hierarchical Vocabulary resource configuration."""

    blueprint_name = "hvocabularies"
    url_prefix = "/hvocabularies"
    routes = {
        "list": "/<type>",
        "item": "/<type>/<path:pid_value>",
    }

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "type": ma.fields.Str(required=True),
    }


class HierarchicalVocabulariesResource(RecordResource):
    pass

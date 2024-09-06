from functools import cached_property

from flask_resources import BaseListSchema, ResponseHandler
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_vocabularies.resources.resource import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.resource import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import fields, post_dump
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from oarepo_vocabularies.services.ui_schema import VocabularyUISchema, VocabularySpecializedUISchema
from marshmallow_oneofschema import OneOfSchema

from importlib_metadata import entry_points


class VocabularySearchRequestArgsSchema(InvenioVocabularySearchRequestArgsSchema):
    parent = fields.List(fields.String(), data_key="h-parent", attribute="h-parent")
    ancestor = fields.List(
        fields.String(), data_key="h-ancestor", attribute="h-ancestor"
    )
    level = fields.List(fields.Integer(), data_key="h-level", attribute="h-level")

    def _deserialize(self, *args, **kwargs):
        ret = super()._deserialize(*args, **kwargs)
        return ret


class VocabularySchemaSelector(OneOfSchema):
    @cached_property
    def type_schemas(self):
        ui_schemas = {
            "vocabulary": VocabularyUISchema,
            "*": VocabularySpecializedUISchema,
        }
        for ep in entry_points().select(group="oarepo_vocabularies.ui_schemas"):
            ui_schemas.update(ep.load())

        return ui_schemas

    def get_obj_type(self, obj):
        from flask_resources import resource_requestctx
        if "type" in obj:
            return "vocabulary"
        vocabulary_type = resource_requestctx.view_args.get("type")
        if vocabulary_type in self.type_schemas:
            return vocabulary_type
        return "*"

    def dump(self, obj, *, many=None, **kwargs):
        ret = super().dump(obj, many=many, **kwargs)
        if ret.get("type") == "*":
            ret.pop("type")
        return ret

class VocabulariesUIResponseHandler(ResponseHandler):
    serializer = LocalizedUIJSONSerializer(
        format_serializer_cls=JSONSerializer,
        object_schema_cls=VocabularySchemaSelector,
        list_schema_cls=BaseListSchema,
    )

    def __init__(self, headers):
        super().__init__(self.serializer, headers)


class VocabulariesResourceConfig(InvenioVocabulariesResourceConfig):
    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers = {
        **InvenioVocabulariesResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": VocabulariesUIResponseHandler(
            headers=etag_headers,
        ),
    }

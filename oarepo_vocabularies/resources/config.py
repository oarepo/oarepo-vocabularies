from flask_resources import BaseListSchema, ResponseHandler
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_vocabularies.resources.resource import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.resource import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import fields
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from oarepo_vocabularies.services.ui_schema import VocabularyUISchema


class VocabularySearchRequestArgsSchema(InvenioVocabularySearchRequestArgsSchema):
    parent = fields.List(fields.String(), data_key="h-parent", attribute="h-parent")
    ancestor = fields.List(
        fields.String(), data_key="h-ancestor", attribute="h-ancestor"
    )
    level = fields.List(fields.Integer(), data_key="h-level", attribute="h-level")

    def _deserialize(self, *args, **kwargs):
        ret = super()._deserialize(*args, **kwargs)
        return ret


class VocabulariesResourceConfig(InvenioVocabulariesResourceConfig):
    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers = {
        **InvenioVocabulariesResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            LocalizedUIJSONSerializer(
                format_serializer_cls=JSONSerializer,
                object_schema_cls=VocabularyUISchema,
                list_schema_cls=BaseListSchema,
            ),
            headers=etag_headers,
        ),
    }

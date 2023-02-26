from invenio_vocabularies.resources.resource import (
    VocabulariesResourceConfig as InvenioVocabulariesResourceConfig,
)
from invenio_vocabularies.resources.resource import (
    VocabularySearchRequestArgsSchema as InvenioVocabularySearchRequestArgsSchema,
)
from marshmallow import fields


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

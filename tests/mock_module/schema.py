import marshmallow.fields as ma_fields
import marshmallow as ma
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_vocabularies.services.schema import i18n_strings

from oarepo_vocabularies.services.schema import VocabularyRelationField, VocabularyRelationSchema
from tests.mock_module.api import Record


class HierarchySchema(VocabularyRelationSchema):
    title = i18n_strings


class MockMetadataSchema(ma.Schema):
    title = ma_fields.Str()
    hierarchy = VocabularyRelationField(HierarchySchema, related_field=Record.relations.hierarchy, many=False)
    hlist = VocabularyRelationField(HierarchySchema, related_field=Record.relations.hierarchy, many=True)


class MockSchema(BaseRecordSchema):
    metadata = ma_fields.Nested(MockMetadataSchema())

import marshmallow.fields as ma_fields
import marshmallow as ma
from invenio_vocabularies.services.schema import i18n_strings

from oarepo_vocabularies.services.schema import VocabularyRelationField, VocabularyRelationSchema
from tests.mock_module.api import Record


class HierarchySchema(VocabularyRelationSchema):
    title = i18n_strings


class MockSchema(ma.Schema):
    title = ma_fields.Str()
    hierarchy = VocabularyRelationField(Record.relations.hierarchy, HierarchySchema, many=False)

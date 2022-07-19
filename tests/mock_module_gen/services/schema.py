import marshmallow as ma
import marshmallow.fields as ma_fields
import marshmallow.validate as ma_valid
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import ValidationError
from marshmallow import validates as ma_validates
from mock_module_gen.records.api import MockModuleGenRecord
from oarepo_vocabularies.services.schema import (
    VocabularyRelationField,
    VocabularyRelationSchema,
)


class Hierarchy(
    VocabularyRelationSchema,
):
    """Hierarchy schema."""

    title = i18n_strings


class Hlist(
    VocabularyRelationSchema,
):
    """Hlist schema."""

    title = i18n_strings


class MockModuleGenSchema(
    BaseRecordSchema,
):
    """MockModuleGenSchema schema."""

    title = ma_fields.String()

    hierarchy = VocabularyRelationField(
        Hierarchy, related_field=MockModuleGenRecord.relations.hierarchy, many=False
    )

    created = ma_fields.Date(dump_only=True)

    updated = ma_fields.Date(dump_only=True)

    hlist = VocabularyRelationField(
        Hlist, related_field=MockModuleGenRecord.relations.hlist, many=True
    )

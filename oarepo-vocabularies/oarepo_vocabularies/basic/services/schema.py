import marshmallow as ma
import marshmallow.fields as ma_fields
import marshmallow.validate as ma_valid
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from invenio_vocabularies.services.schema import BaseVocabularySchema
from marshmallow import ValidationError
from marshmallow import validates as ma_validates


class OARepoVocabulariesBasicSchema(
    BaseVocabularySchema,
):
    """OARepoVocabulariesBasicSchema schema."""

    type = ma_fields.Str(required=True, attribute="type.id")

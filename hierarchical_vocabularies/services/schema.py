# from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_vocabularies.services.schema import VocabularySchema
from marshmallow import EXCLUDE, RAISE, Schema, fields, validate


class HVocabularySchema(VocabularySchema):
    """Service schema for vocabulary records.."""

    relatedURI = fields.Dict(allow_none=True, keys=fields.Str(), values=fields.Str())
    alpha3Code = fields.Dict(allow_none=True, keys=fields.Str(), values=fields.Str())
    nonpreferredLabels = fields.List(
        fields.Dict(allow_none=True, keys=fields.Str(), values=fields.Str())
    )
    # nameTranslated = fields.Str(allow_none=True)
    nameType = fields.Str()
    fullName = fields.Str()
    acronym = fields.Str()
    ICO = fields.Number()
    RID = fields.Str()
    marcCode = fields.Str()
    dataCiteCode = fields.Str()
    aliases = fields.List(fields.Str())
    CEA = fields.Boolean()
    contexts = fields.List(fields.Str())
    pair = fields.Str()
    hint = fields.Dict(allow_none=True, keys=fields.Str(), values=fields.Str())
    coarType = fields.Str()
    dataCiteType = fields.Str()

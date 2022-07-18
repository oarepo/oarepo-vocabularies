import marshmallow as ma
import marshmallow.fields as ma_fields
import marshmallow.validate as ma_valid
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from marshmallow import ValidationError
from marshmallow import validates as ma_validates


class Properties(
    ma.Schema,
):
    """Properties schema."""

    id = ma_fields.String()


class HlistSchema(
    ma.Schema,
):
    """HlistSchema schema."""

    id = ma_fields.String()


class MockModuleGenSchema(
    BaseRecordSchema,
):
    """MockModuleGenSchema schema."""

    title = ma_fields.String()

    hierarchy = ma_fields.Nested(lambda: Properties())

    created = ma_fields.Date(dump_only=True)

    updated = ma_fields.Date(dump_only=True)

    hlist = ma_fields.List(ma_fields.Nested(lambda: HlistSchema()))

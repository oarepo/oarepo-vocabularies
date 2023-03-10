import marshmallow as ma
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import fields as ma_fields


class HierarchySchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String()
    level = ma_fields.Integer()
    title = ma_fields.List(i18n_strings)
    ancestors = ma_fields.List(ma_fields.String())

from functools import partial

import marshmallow as ma
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import fields as ma_fields
from marshmallow_utils.fields import NestedAttribute
from oarepo_runtime.cf import InlinedCustomFieldsSchemaMixin


class VocabularySchema(InlinedCustomFieldsSchemaMixin, InvenioVocabularySchema):
    CUSTOM_FIELDS_VAR = "OAREPO_VOCABULARIES_CUSTOM_CF"
    hierarchy = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HierarchySchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String()
    level = ma_fields.Integer()
    title = ma_fields.List(i18n_strings)
    ancestors = ma_fields.List(ma_fields.String())
    ancestors_or_self = ma_fields.List(ma_fields.String())

from functools import partial

import marshmallow as ma
from flask import current_app
from flask_babelex import get_locale
from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow import fields as ma_fields
from marshmallow_utils.fields import NestedAttribute
from oarepo_runtime.cf import InlinedCustomFieldsSchemaMixin
from oarepo_runtime.ui.marshmallow import LocalizedDateTime


class VocabularyI18nStrUIField(ma_fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        locale = get_locale().language
        if locale in value:
            return value[locale]
        locale = current_app.config["BABEL_DEFAULT_LOCALE"]
        if locale in value:
            return value[locale]
        return next(iter(value.values()))


class HierarchyUISchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String()
    level = ma_fields.Integer()
    title = ma_fields.List(VocabularyI18nStrUIField())
    ancestors = ma_fields.List(ma_fields.String())
    ancestors_or_self = ma_fields.List(ma_fields.String())


class VocabularyUISchema(InlinedCustomFieldsSchemaMixin, InvenioVocabularySchema):
    CUSTOM_FIELDS_VAR = "OAREPO_VOCABULARIES_CUSTOM_CF"
    hierarchy = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    created = LocalizedDateTime(dump_only=True)
    updated = LocalizedDateTime(dump_only=True)
    links = ma.fields.Raw(dump_only=True)
    title = VocabularyI18nStrUIField()
    type = ma.fields.Raw(dump_only=True)

from functools import partial

import marshmallow as ma
from flask import current_app
from flask_babelex import get_locale
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow import fields as ma_fields
from oarepo_runtime.cf import InlinedCustomFieldsSchemaMixin
from oarepo_runtime.services.schema.cf import CustomFieldsSchemaUI
from oarepo_runtime.services.schema.ui import LocalizedDateTime


class VocabularyI18nStrUIField(ma_fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        locale = self.context["locale"]
        if locale:
            language = locale.language
            if language in value:
                return value[language]
        locale = current_app.config["BABEL_DEFAULT_LOCALE"]
        if locale in value:
            return value[locale]
        return next(iter(value.values()))

    def get_locale(self):
        if "locale" in self.context:
            return self.context["locale"]
        locale = get_locale()
        self.context["locale"] = locale
        return locale


class HierarchyUISchema(ma.Schema):
    """HierarchySchema schema."""

    parent = ma_fields.String()
    level = ma_fields.Integer()
    title = ma_fields.List(VocabularyI18nStrUIField())
    ancestors = ma_fields.List(ma_fields.String())
    ancestors_or_self = ma_fields.List(ma_fields.String())


class VocabularyUISchema(InlinedCustomFieldsSchemaMixin, InvenioVocabularySchema):
    CUSTOM_FIELDS_VAR = "OAREPO_VOCABULARIES_CUSTOM_CF"
    hierarchy = ma_fields.Nested(
        partial(CustomFieldsSchemaUI, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    created = LocalizedDateTime(dump_only=True)
    updated = LocalizedDateTime(dump_only=True)
    links = ma.fields.Raw(dump_only=True)
    title = VocabularyI18nStrUIField()
    type = ma.fields.Raw(dump_only=True)

    def dump(self, *args, **kwargs):
        return super().dump(*args, **kwargs)

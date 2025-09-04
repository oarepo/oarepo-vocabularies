import copy
from functools import partial

import marshmallow as ma
import marshmallow_utils
from flask import current_app
from invenio_i18n import get_locale

# from oarepo_runtime.services.schema.cf import CustomFieldsSchemaUI  # udelat znova
# from oarepo_runtime.services.schema.ui import LocalizedDateTime  # copy paste z modelu
from invenio_records_resources.services.custom_fields.schema import (
    CustomFieldsSchemaUI as InvenioCustomFieldsSchemaUI,
)
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow import fields as ma_fields


class LocalizedDateTime(ma.fields.Field):
    """
    A Marshmallow field that provides localized datetime formatting.
    """

    def __init__(self, attribute, **kwargs):
        super().__init__(**kwargs)
        self.attribute = attribute

    def _serialize(self, value, attr, obj, **kwargs):
        return {
            f"{self.attribute}_l10n_long": marshmallow_utils.fields.FormatDate(
                attribute=self.attribute,
                format="long",
            ),
            f"{self.attribute}_l10n_medium": marshmallow_utils.fields.FormatDate(
                attribute=self.attribute,
                format="medium",
            ),
            f"{self.attribute}_l10n_short": marshmallow_utils.fields.FormatDate(
                attribute=self.attribute,
                format="short",
            ),
            f"{self.attribute}_l10n_full": marshmallow_utils.fields.FormatDate(
                attribute=self.attribute,
                format="full",
            ),
        }


class CustomFieldsSchemaUI(InvenioCustomFieldsSchemaUI):
    def _serialize(self, obj, **kwargs):
        self._schema.context.update(self.context)
        return super()._serialize(obj, **kwargs)

    def _deserialize(self, data, **kwargs):
        self._schema.context.update(self.context)
        return super()._deserialize(data, **kwargs)


class VocabularyI18nStrUIField(ma_fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        # locale = self.context["locale"]
        locale = self.get_locale()
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


class VocabularyUISchema(InvenioVocabularySchema):
    CUSTOM_FIELDS_VAR = "VOCABULARIES_CF"
    hierarchy = ma_fields.Nested(
        partial(CustomFieldsSchemaUI, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    created = LocalizedDateTime("created", dump_only=True)
    updated = LocalizedDateTime("updated", dump_only=True)
    links = ma.fields.Raw(dump_only=True)
    title = VocabularyI18nStrUIField()
    type = ma.fields.Raw(dump_only=True)
    description = VocabularyI18nStrUIField()
    props = ma.fields.Dict(keys=ma.fields.String(), values=ma.fields.String())


class VocabularySpecializedUISchema(VocabularyUISchema):
    @ma.post_dump(pass_many=False, pass_original=True)
    def dump_extra_fields(self, data, original_data, **kwargs):
        for k, v in original_data.items():
            if k not in data:
                data[k] = copy.deepcopy(v)
        return data

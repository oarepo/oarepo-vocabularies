import marshmallow as ma
from invenio_vocabularies.services.schema import i18n_strings
from marshmallow import fields as ma_fields
from flask_babelex import get_locale
from flask import current_app


class I18nStrUIField(ma_fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return None
        locale = get_locale()
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
    title = ma_fields.List(I18nStrUIField())
    ancestors = ma_fields.List(ma_fields.String())

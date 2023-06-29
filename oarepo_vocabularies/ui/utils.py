from flask import current_app
from marshmallow import Schema, fields
from marshmallow.schema import SchemaMeta
from marshmallow_utils.fields import NestedAttribute
from flask_babelex import lazy_gettext as _

def dump_empty(schema_or_field):
    """Return a full json-compatible dict with empty values.

    NOTE: This is only needed because the frontend needs it.
          This might change soon.
    """
    if isinstance(schema_or_field, (Schema,)):
        schema = schema_or_field
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, SchemaMeta):
        # Nested fields can pass a Schema class (SchemaMeta)
        # or a Schema instance.
        # Schema classes need to be instantiated to get .fields
        schema = schema_or_field()
        return {k: dump_empty(v) for (k, v) in schema.fields.items()}
    if isinstance(schema_or_field, fields.List):
        field = schema_or_field
        return [dump_empty(field.inner)]
    if isinstance(schema_or_field, NestedAttribute):
        field = schema_or_field
        return dump_empty(field.nested)

    return None

def load_custom_fields():
        """Load custom fields configuration."""
        conf = current_app.config
        conf_backend = {
            cf.name: cf for cf in conf.get("OAREPO_VOCABULARIES_HIERARCHY_CF", [])
        }

        conf_ui = [
            {
                "section": _("Vocabulary hierarchy"),
                "fields": [
                    {
                        "field": "hierarchy",
                        "ui_widget": "TextInput",
                        "props": {
                            "label": _("Hierarchy"),
                            "title": {
                                "label": _("Hierarchy title"),
                                "placeholder": _("Add the title..."),
                                "description": _(
                                    "Add the title of the hierarchy"
                                ),
                            },
                            "icon": "lab",
                        },
                    }
                ],
            }
        ]

        return {
            "ui": conf_ui,
        }
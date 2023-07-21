from flask_babelex import lazy_gettext as _


def load_custom_fields():
    """Load custom fields configuration."""
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
                            "description": _("Add the title of the hierarchy"),
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

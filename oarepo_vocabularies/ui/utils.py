# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI utils."""

from __future__ import annotations

from invenio_i18n import lazy_gettext as _


def load_custom_fields() -> dict:
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

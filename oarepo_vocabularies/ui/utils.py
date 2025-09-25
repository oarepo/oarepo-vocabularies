#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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

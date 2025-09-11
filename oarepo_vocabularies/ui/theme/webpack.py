#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Webpack theme definition."""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "oarepo_vocabularies_search": "./js/oarepo_vocabularies_ui/search/app.js",
                "oarepo_vocabularies_ui_components": "./js/oarepo_vocabularies_ui/custom-components.js",
                "oarepo_vocabularies_detail": "./js/oarepo_vocabularies_ui/detail/app.js",
                "oarepo_vocabularies_form": "./js/oarepo_vocabularies_ui/form/app.js",
            },
            "dependencies": {},
            "devDependencies": {},
            "aliases": {
                "@translations/oarepo_vocabularies_ui": "./translations/oarepo_vocabularies_ui",
                "@js/oarepo_vocabularies": "js/oarepo_vocabularies_ui",
            },
        }
    },
)

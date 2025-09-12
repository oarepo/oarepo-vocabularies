# Copyright (c) 2022 Miroslav Bauer
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
"""oarepo-vocabularies UI extension."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from invenio_base.utils import obj_or_import_string

from oarepo_vocabularies.proxies import current_type_service
from oarepo_vocabularies.ui import config

if TYPE_CHECKING:
    from flask import Flask


class InvenioVocabulariesAppExtension:
    """Flask extension for oarepo-vocabularies UI."""

    def __init__(self, app: Flask | None = None):
        """Extension for oarepo-vocabularies UI."""
        if app:
            self.init_config(app)
            self.init_app(app)
            self.init_resource(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the app."""
        app.extensions["oarepo_vocabularies_ui"] = self

    def init_resource(self, app: Flask) -> None:
        """Initialize vocabulary resources."""
        # Import and check for None so linter does not complain
        resource_cls = obj_or_import_string(app.config["OAREPO_VOCABULARIES_UI_RESOURCE"])
        assert resource_cls is not None, "OAREPO_VOCABULARIES_UI_RESOURCE must be set"  # noqa: S101

        config_cls = obj_or_import_string(app.config["OAREPO_VOCABULARIES_UI_RESOURCE_CONFIG"])
        assert config_cls is not None, "OAREPO_VOCABULARIES_UI_RESOURCE_CONFIG must be set"  # noqa: S101

        self.resource = resource_cls(
            config=config_cls(),
        )

        type_resource_cls = obj_or_import_string(app.config["VOCABULARY_TYPE_UI_RESOURCE"])
        assert type_resource_cls is not None, "VOCABULARY_TYPE_UI_RESOURCE must be set"  # noqa: S101

        config_cls = obj_or_import_string(app.config["VOCABULARY_TYPE_UI_RESOURCE_CONFIG"])
        assert config_cls is not None, "VOCABULARY_TYPE_UI_RESOURCE_CONFIG must be set"  # noqa: S101

        self.type_resource = type_resource_cls(
            config=config_cls(),
            service=current_type_service,
        )

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        for identifier in dir(config):
            if re.match("^[A-Z_]*$", identifier) and not identifier.startswith("_"):
                app.config.setdefault(identifier, getattr(config, identifier))

        app.config.setdefault("OAREPO_UI_LESS_COMPONENTS", []).extend(config.OAREPO_UI_LESS_COMPONENTS)


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    from oarepo_ui.proxies import current_oarepo_ui

    from oarepo_vocabularies.ui.proxies import current_vocabularies_ui

    with app.app_context():
        current_oarepo_ui.register_resource(current_vocabularies_ui.resource)
        current_oarepo_ui.register_resource(current_vocabularies_ui.type_resource)

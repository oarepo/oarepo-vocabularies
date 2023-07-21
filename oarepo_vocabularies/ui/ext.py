# Copyright (c) 2022 Miroslav Bauer
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import re

from invenio_base.utils import obj_or_import_string

from oarepo_vocabularies.proxies import current_type_service
from oarepo_vocabularies.ui import config as config


class InvenioVocabulariesAppExtension:
    def __init__(self, app=None):
        if app:
            self.init_config(app)
            self.init_app(app)
            self.init_resource(app)

    def init_app(self, app):
        app.extensions["oarepo_vocabularies_ui"] = self

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.resource = obj_or_import_string(
            app.config["OAREPO_VOCABULARIES_UI_RESOURCE"]
        )(
            config=obj_or_import_string(
                app.config["OAREPO_VOCABULARIES_UI_RESOURCE_CONFIG"]
            )(),
        )

        self.type_resource = obj_or_import_string(
            app.config["VOCABULARY_TYPE_UI_RESOURCE"]
        )(
            config=obj_or_import_string(
                app.config["VOCABULARY_TYPE_UI_RESOURCE_CONFIG"]
            )(),
            service=current_type_service,
        )

    def init_config(self, app):
        """Initialize configuration."""
        for identifier in dir(config):
            if re.match("^[A-Z_]*$", identifier) and not identifier.startswith("_"):
                app.config.setdefault(identifier, getattr(config, identifier))

        app.config.setdefault("OAREPO_UI_LESS_COMPONENTS", []).extend(
            config.OAREPO_UI_LESS_COMPONENTS
        )

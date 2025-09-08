#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from oarepo_vocabularies.ui.proxies import current_ui


def create_blueprint(app):
    """Blueprint for the routes and resources provided by current ui's resource."""
    with app.app_context():
        app.extensions["oarepo_ui"].register_resource(current_ui.resource)
        return current_ui.resource.as_blueprint()


def create_vocabulary_type_blueprint(app):
    with app.app_context():
        app.extensions["oarepo_ui"].register_resource(current_ui.type_resource)
        return current_ui.type_resource.as_blueprint()


def create_vocabulary_awards_blueprint(app):
    with app.app_context():
        app.extensions["oarepo_ui"].register_resource(current_ui.awards_resource)
        return current_ui.awards_resource.as_blueprint()

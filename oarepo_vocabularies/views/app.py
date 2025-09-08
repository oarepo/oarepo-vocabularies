#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask import Blueprint


def create_app_blueprint(app):
    blueprint = Blueprint("oarepo_vocabularies", __name__, template_folder="templates")
    blueprint.record_once(init_create_app_blueprint)
    return blueprint


def init_create_app_blueprint(state):
    """Init app."""
    app = state.app
    ext = app.extensions["oarepo-vocabularies"]

    # Register service.
    sregistry = app.extensions["invenio-records-resources"].registry
    if ext.type_service.config.service_id not in sregistry._services:
        sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

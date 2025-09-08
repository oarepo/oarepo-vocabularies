#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
def create_api_blueprint(app):
    """Create MymodelRecord blueprint."""
    blueprint = app.extensions["oarepo-vocabularies"].type_resource.as_blueprint()
    blueprint.record_once(init_create_api_blueprint)
    return blueprint


def init_create_api_blueprint(state):
    """Init app."""
    app = state.app
    ext = app.extensions["oarepo-vocabularies"]

    # Register service.
    sregistry = app.extensions["invenio-records-resources"].registry

    if ext.type_service.config.service_id not in sregistry._services:
        sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

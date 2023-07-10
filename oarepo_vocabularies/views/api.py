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
    sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

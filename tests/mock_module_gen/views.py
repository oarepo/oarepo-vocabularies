def create_blueprint_from_app(app):
    """Create  blueprint."""
    blueprint = app.extensions["mock_module_gen"].resource.as_blueprint()
    blueprint.record_once(init)
    return blueprint


def init(state):
    """Init app."""
    app = state.app
    ext = app.extensions["mock_module_gen"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(ext.service, service_id="mock_module_gen")

    # Register indexer
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.service.indexer, indexer_id="mock_module_gen")

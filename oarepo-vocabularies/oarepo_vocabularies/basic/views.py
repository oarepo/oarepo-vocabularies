def create_basic_blueprint_from_app(app):
    """Create  blueprint."""
    blueprint = app.extensions["oarepo-vocabularies-basic"].resource.as_blueprint()
    blueprint.record_once(init)
    return blueprint


def init(state):
    """Init app."""
    app = state.app
    ext = app.extensions["oarepo-vocabularies-basic"]

    # register service
    sregistry = app.extensions["invenio-records-resources"].registry
    sregistry.register(ext.service, service_id="oarepo-vocabularies-basic")

    # Register indexer
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.service.indexer, indexer_id="oarepo-vocabularies-basic")

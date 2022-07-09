def create_basic_blueprint_from_app(app):
    """Create  blueprint."""
    return app.extensions["oarepo-vocabularies-basic"].resource.as_blueprint()

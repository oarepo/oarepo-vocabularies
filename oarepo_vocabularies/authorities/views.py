def create_authorities_blueprint(app):
    """Create authorities blueprint."""
    blueprint = app.extensions[
        "oarepo-vocabularies-authorities"
    ].resource.as_blueprint()
    return blueprint

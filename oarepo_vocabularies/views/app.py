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
    sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

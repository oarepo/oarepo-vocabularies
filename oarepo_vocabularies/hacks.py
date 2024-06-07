from invenio_records_resources.proxies import current_service_registry

from oarepo_vocabularies.services.service import VocabulariesService


def patch_invenio_vocabulary_service(app):
    invenio_vocabularies = app.extensions.get("invenio-vocabularies")
    if not invenio_vocabularies:
        return

    # get wrapper
    previous_service = invenio_vocabularies.service
    new_service = VocabulariesService(config=previous_service.config)

    # register the wrapper
    invenio_vocabularies.service = new_service
    invenio_vocabularies.resource.service = new_service

    # replace the wrapper in the service registry -
    # need to use _services as add_service checks if the service is already
    # registered. If it is not, the code above is sufficient as when
    # the invenio vocabularies blueprint is started, it will register
    # the service set above.
    with app.app_context():
        if "vocabularies" in current_service_registry._services:
            current_service_registry._services["vocabularies"] = new_service

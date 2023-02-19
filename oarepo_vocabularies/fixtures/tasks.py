from celery import shared_task
from invenio_records_resources.proxies import current_service_registry
from invenio_access.permissions import system_identity


# taken from invenio-rdm-records, will be removed when/if this code gets to invenio vocabularies
# https://github.com/inveniosoftware/invenio-rdm-records/blob/master/invenio_rdm_records/fixtures/tasks.py

@shared_task
def create_vocabulary_record(service_str, data):
    """Create a vocabulary record."""
    service = current_service_registry.get(service_str)
    service.create(system_identity, data)

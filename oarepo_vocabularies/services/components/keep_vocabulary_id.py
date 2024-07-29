from flask import current_app
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service

from ..custom_fields.hierarchy import HierarchyCF


class KeepVocabularyIdComponent(ServiceComponent):

    def update(self, identity, data=None, record=None, **kwargs):
        if "id" not in data:
            data["id"] = record["id"]

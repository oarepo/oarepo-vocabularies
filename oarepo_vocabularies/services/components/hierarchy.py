from flask import current_app
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service

from ..custom_fields.hierarchy import HierarchyCF


class HierarchyComponent(ServiceComponent):
    CONFIG_CF_KEY = "OAREPO_VOCABULARIES_HIERARCHY_CF"

    def create(self, identity, data=None, record=None, **kwargs):
        self.set_hierarchy(identity, record)

    def update(self, identity, data=None, record=None, **kwargs):
        self.set_hierarchy(identity, record)

    def set_hierarchy(self, identity, record):
        record.hierarchy = record.setdefault("hierarchy", {})
        if "parent" in record.hierarchy:
            parent = self.get_parent(identity, record)
        else:
            parent = None
        for cf in current_app.config[self.CONFIG_CF_KEY]:
            if isinstance(cf, HierarchyCF):
                cf.update(record, parent)

    def get_parent(self, identity, record):
        parent = record.hierarchy.get("parent", None)
        if not parent:
            return None
        return current_service.read(identity, (record.type.id, parent)).data

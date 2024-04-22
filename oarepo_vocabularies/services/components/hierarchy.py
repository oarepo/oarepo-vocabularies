from flask import current_app
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service

from ..custom_fields.hierarchy import HierarchyCF


class HierarchyComponent(ServiceComponent):
    CONFIG_CF_KEY = "OAREPO_VOCABULARIES_HIERARCHY_CF"

    def create(self, identity, data=None, record=None, **kwargs):
        self.set_hierarchy(identity, record)
        record.hierarchy["leaf"] = True
        self.set_parent_leaf(identity, record, is_leaf=False)

    def update(self, identity, data=None, record=None, **kwargs):
        self.set_hierarchy(identity, record)
        self.set_leaf(identity, record)

    def delete(self, identity, record=None, **kwargs):
        self.set_parent_leaf(identity, record, exclude_child=record["id"])
        return record

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
        return current_service.read(identity, (record.type.id, parent))._record

    def set_leaf(
        self, identity, record, exclude_child=None, commit=False, is_leaf=None
    ):
        # refresh to make sure the scan will return everything. This is a performance bottleneck
        # but we can not do it without this as we do not have a way to get the parent
        # directly from the database
        if is_leaf is not None:
            if record.hierarchy.get("leaf", None) is not is_leaf:
                record.hierarchy["leaf"] = is_leaf
                if commit:
                    record.commit()
        else:
            current_service.indexer.refresh()
            children = list(
                current_service.scan(identity, params={"h-parent": record["id"]})
            )
            if exclude_child:
                children = [child for child in children if child["id"] != exclude_child]
            updated_is_leaf = len(children) == 0
            if record.hierarchy.get("leaf", None) is not updated_is_leaf:
                record.hierarchy["leaf"] = updated_is_leaf
                if commit:
                    record.commit()

    def set_parent_leaf(self, identity, record, exclude_child=None, is_leaf=None):
        if "parent" in record.hierarchy:
            parent = self.get_parent(identity, record)
            self.set_leaf(
                identity,
                parent,
                exclude_child=exclude_child,
                commit=True,
                is_leaf=is_leaf,
            )

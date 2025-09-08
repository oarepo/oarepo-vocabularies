#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_db import db
from invenio_records.systemfields import SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin
from oarepo_runtime.records.systemfields.selectors import PathSelector

from oarepo_vocabularies.records.models import VocabularyHierarchy

from .helpers import HierarchyObject


class HierarchySystemField(MappingSystemFieldMixin, SystemField):
    def __get__(self, record, owner=None) -> HierarchyObject:
        if record is None:
            return self

        if not hasattr(record, "_hierarchy_cache"):
            record._hierarchy_cache = HierarchyObject(record)

        return record._hierarchy_cache

    @property
    def mapping(self):
        return {
            self.key: {
                "type": "object",
                "enabled": True,
                "properties": {
                    "parent": {
                        "type": "keyword",
                    },
                    "level": {"type": "integer"},
                    "titles": {"type": "object", "enabled": False},
                    "ancestors": {"type": "keyword"},
                    "ancestors_or_self": {"type": "keyword"},
                    "leaf": {"type": "boolean"},
                },
            }
        }

    def pre_commit(self, record):
        hierarchy_obj = self.__get__(record)
        hierarchy_obj._hierarchy_data.fix_hierarchy_on_self()

        # Store information about whether we need to fix descendants
        # We have new parent or we had no parent
        parent_changed = record.parent.uuid != record.parent.previous_uuid or (
            record.parent.uuid and not record.parent.previous_uuid
        )

        hierarchy_obj._hierarchy_data.update_parent_leaf_status(record.parent)

        if parent_changed:
            hierarchy_obj._hierarchy_data.fix_hierarchy_down()

    def pre_delete(self, record, force=False):
        hierarchy_obj = self.__get__(record)

        hierarchy_obj._hierarchy_data.update_parent_leaf_status(record.parent)

        # update children hierarchy
        hierarchy_obj._hierarchy_data.fix_hierarchy_down_on_delete()

        # delete after children are updated
        hierarchy_entry = VocabularyHierarchy.query.get(record.id)
        if hierarchy_entry:
            db.session.delete(hierarchy_entry)

    def pre_dump(self, record, data, dumper=None):
        hierarchy_obj = self.__get__(record)
        data[self.key] = hierarchy_obj.to_dict()


class HierarchyPartSelector(PathSelector):
    level = 0

    def __init__(self, *paths, level=None, **kwargs):
        super().__init__(*paths)
        if level is not None:
            self.level = level
        if not self.paths:
            raise ValueError("At least one path must be set")

    def select(self, data):
        parts = super().select(data)

        elements = []
        for dg in parts:
            ids = dg["hierarchy"]["ancestors_or_self"]
            titles = dg["hierarchy"]["title"]
            if len(ids) > self.level:
                elements.append({"id": ids[-1 - self.level], "title": titles[-1 - self.level]})
        return elements

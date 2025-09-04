from typing import Any, Protocol

from invenio_records.systemfields import DictField, SystemField

from .helpers import HierarchyObject


# TODO: move to runtime
class Selector(Protocol):
    def select(self, record) -> list[Any]:
        return []


class PathSelector(Selector):
    def __init__(self, *paths):
        self.paths = [x.split(".") for x in paths]

    def select(self, record):
        ret = []
        for path in self.paths:
            for rec in getter(record, path):
                ret.append(rec)
        return ret


def getter(data, path: list):
    if len(path) == 0:
        if isinstance(data, list):
            yield from data
        else:
            yield data
    elif isinstance(data, dict):
        if path[0] in data:
            yield from getter(data[path[0]], path[1:])
    elif isinstance(data, list):
        for item in data:
            yield from getter(item, path)


class HierarchySystemField(SystemField):
    def __init__(self, key=None, clear_none=False, create_if_missing=True):
        self.clear_none = clear_none
        self.create_if_missing = create_if_missing
        super().__init__(key=key)

        self._dict_field = DictField(
            key=key, clear_none=clear_none, create_if_missing=create_if_missing
        )

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self._dict_field.__set_name__(owner, name)

    def __get__(self, record, owner=None) -> HierarchyObject:
        if record is None:
            return self

        if not hasattr(record, "_hierarchy_cache"):
            record._hierarchy_cache = HierarchyObject(self._dict_field, record)

        return record._hierarchy_cache

    def pre_commit(self, record):
        hierarchy_obj = self.__get__(record)
        hierarchy_obj.fix_hierarchy_on_self()

        # Store information about whether we need to fix descendants
        # We have new parent or we had no parent
        parent_changed = record.parent.uuid != record.parent.previous_uuid or (
            record.parent.uuid and not record.parent.previous_uuid
        )

        hierarchy_obj.update_parent_leaf_status()

        if parent_changed:
            hierarchy_obj.fix_hierarchy_down()


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
                elements.append(
                    {"id": ids[-1 - self.level], "title": titles[-1 - self.level]}
                )
        return elements

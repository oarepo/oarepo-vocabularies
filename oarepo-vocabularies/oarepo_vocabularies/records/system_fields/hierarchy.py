from typing import List

from invenio_records.systemfields import SystemField


class LevelSystemField(SystemField):
    def __get__(self, record, owner=None):
        if record is None:
            return self
        id_ = record.get('id')
        if not id_:
            return 0
        return len(id_.split('/'))


class HierarchyPathSystemField(SystemField):
    def __get__(self, record, owner=None):
        if record is None:
            return self
        return record.get('id')

    @staticmethod
    def get_from_id(id_):
        return id_

    @staticmethod
    def get_parent_id_from_id(id_):
        return '/'.join(id_[1].split('/')[:-1])

    @staticmethod
    def paths_to_id(paths: List[str]):
        return paths

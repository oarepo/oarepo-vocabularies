from invenio_db import db
from invenio_records.systemfields import DictField, SystemField

from oarepo_vocabularies.records.models import VocabularyHierarchy

from .helpers import ParentObject


class ParentSystemField(SystemField):
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

    def __get__(self, record, owner=None) -> ParentObject:
        if not hasattr(record, "_parent_cache"):
            record._parent_cache = ParentObject(self._dict_field, record)

        return record._parent_cache

    def __set__(self, record, value):
        self.__get__(record).set(value)

    def pre_commit(self, record):
        cache = self.__get__(record)

        parent = record.relations.parent()
        if parent:
            parent_uuid = parent.id
            self_uuid = record.id

            hierarchy_entry = VocabularyHierarchy.query.get(self_uuid)
            if hierarchy_entry:
                # Update existing row
                hierarchy_entry.parent_id = parent_uuid
            else:
                # Insert new row
                hierarchy_entry = VocabularyHierarchy(
                    id=self_uuid,
                    parent_id=parent_uuid,
                )
                db.session.add(hierarchy_entry)

            # Use flush so it stays inside the same transaction
            db.session.flush()
        elif parent is None and cache.previous_uuid and not cache.uuid:
            # parent was removed, we need to delete row in DB
            row = (
                db.session.query(VocabularyHierarchy)
                .filter(
                    VocabularyHierarchy.id == record.id,
                    VocabularyHierarchy.parent_id == cache.previous_uuid,
                )
                .one()
            )  # there is always will be one row, but this will catch any mistakes

            # remove also from db
            if row:
                db.session.delete(row)
                db.session.flush()

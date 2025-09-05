from invenio_db import db
from invenio_records.systemfields import DictField, SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

from oarepo_vocabularies.records.models import VocabularyHierarchy

from .helpers import ParentObject


class ParentSystemField(MappingSystemFieldMixin, SystemField):
    def __init__(self, key=None, clear_none=False, create_if_missing=True):
        self.clear_none = clear_none
        self.create_if_missing = create_if_missing
        super().__init__(key=key)

        self._dict_field = DictField(
            key=key, clear_none=clear_none, create_if_missing=create_if_missing
        )

    @property
    def mapping(self):
        return {
            self.key: {
                "type": "object",
                "enabled": True,
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "object", "enabled": False},
                },
            }
        }

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self._dict_field.__set_name__(owner, name)

    def __get__(self, record, owner=None) -> ParentObject:
        if record is None:
            return self

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
                if hierarchy_entry.parent_id != parent_uuid:
                    hierarchy_entry.parent_id = parent_uuid

                # check if title is the same
                if record.get("title") != hierarchy_entry.titles[0]:
                    hierarchy_entry.titles[0] = record.get("title")
            else:
                # Insert new row
                hierarchy_entry = VocabularyHierarchy(
                    id=self_uuid,
                    parent_id=parent_uuid,
                    pid=record.get("id"),
                    titles=[record.get("title")],
                )
                db.session.add(hierarchy_entry)

            # Use flush so it stays inside the same transaction
            db.session.flush()
        elif parent is None and cache.previous_uuid and not cache.uuid:
            # parent was removed, we need to update row in DB
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
                row.parent_id = None
                db.session.add(row)
                db.session.flush()

    def pre_delete(self, record, force=False):
        cache = self.__get__(record)

        cache._previous_parent_uuid = cache.uuid
        cache._parent_uuid = None
        cache._parent_id = None
        self_uuid = record.id

        # If record has any children, set their parent to parent of the deleted record
        direct_children = VocabularyHierarchy._get_direct_subterms_ids(self_uuid)

        for child_id in direct_children:
            child_entry = VocabularyHierarchy.query.get(child_id)
            if child_entry:
                child_entry.parent_id = cache.previous_uuid
                db.session.add(child_entry)

        db.session.flush()

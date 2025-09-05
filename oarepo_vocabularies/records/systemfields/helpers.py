from invenio_db import db
from invenio_vocabularies.records.api import Vocabulary

from oarepo_vocabularies.records.models import VocabularyHierarchy


class ParentObject:
    def __init__(self, dict_field, record):
        self._dict_field = dict_field
        self._record = record
        self._previous_parent_uuid = None
        self._parent_uuid = None
        self._parent_id = None
        self._cached = False

    @property
    def uuid(self):
        if not self._cached:
            self._get_from_record()

        return self._parent_uuid

    @property
    def previous_uuid(self):
        if not self._cached:
            self._get_from_record()
        return self._previous_parent_uuid

    def _get_from_record(self):
        parent = self._record.relations.parent()

        if parent:
            self._parent_uuid = parent.id
            self._previous_parent_uuid = (
                db.session.query(VocabularyHierarchy.parent_id)
                .filter(VocabularyHierarchy.id == self._record.id)
                .scalar()
            )
            self._parent_id = parent["id"]

            self._cached = True
        else:
            # there is no parent on record -> current is none and previous parent will be what we have in current
            self._previous_parent_uuid = self._parent_uuid
            self._parent_uuid = None
            self._parent_id = None
            self._cached = True

    def set(self, value):
        if not self._cached:
            self._get_from_record()

        self._dict_field.__set__(self._record, value)
        parent_id = value.get("id")

        # no parent
        if not parent_id:
            self._previous_parent_uuid = self._parent_uuid
            self._parent_id = None
            self._parent_uuid = None
            return

        # changed parent
        if parent_id != self._parent_id:
            self._parent_id = parent_id
            self._previous_parent_uuid = self._parent_uuid  # current will be previous
            self._parent_uuid = (
                Vocabulary.pid.with_type_ctx(self._record["type"]["id"])
                .resolve(parent_id)
                .id
            )
            self._cached = True


class HierarchyObject:
    def __init__(self, record):
        self._record = record
        self._hierarchy_data = self._record.model.hierarchy_metadata

        if self._hierarchy_data is None:
            self._hierarchy_data = VocabularyHierarchy(
                id=self._record.id,
                parent_id=self._record.parent.uuid,
                pid=self._record["id"],
                titles=[self._record.get("title")],
            )

    @property
    def data(self):
        """Get the hierarchy data dictionary"""
        return self._hierarchy_data

    @property
    def to_dict(self):
        return {
            "level": self._hierarchy_data.level,
            "titles": self._hierarchy_data.titles,
            "ancestors": self._hierarchy_data.ancestors,
            "ancestors_or_self": self._hierarchy_data.ancestors_or_self,
            "leaf": self._hierarchy_data.leaf,
        }

    def query_subterms(self):
        """Get direct subterms of this record"""
        subterm_ids = self._hierarchy_data._get_direct_subterms_ids(self._record.id)
        return Vocabulary.get_records(subterm_ids)

    def query_descendants(self):
        """Get all descendants (children, grandchildren, etc.) of this record"""
        descendants_ids = self._hierarchy_data._get_subterms_ids(self._record.id)
        return Vocabulary.get_records(descendants_ids)

    def query_ancestors(self):
        """Get all ancestors of this record"""
        ancestors_ids = self._hierarchy_data._get_ancestors_ids(self._record.id)
        return Vocabulary.get_records(ancestors_ids)

    @property
    def level(self):
        return self._hierarchy_data.level

    @property
    def leaf(self):
        return self._hierarchy_data.leaf

    @property
    def titles(self):
        return self._hierarchy_data.titles

    @property
    def ancestors_ids(self):
        return self._hierarchy_data.ancestors

    @property
    def ancestors_or_self_ids(self):
        return self._hierarchy_data.ancestors_or_self

    @property
    def parent_id(self):
        return (
            self._hierarchy_data.ancestors[0]
            if self._hierarchy_data.ancestors
            else None
        )

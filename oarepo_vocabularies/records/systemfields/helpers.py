from invenio_db import db
from invenio_vocabularies.records.api import Vocabulary
from sqlalchemy.orm import aliased

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
    def __init__(self, dict_field, record):
        self._dict_field = dict_field
        self._record = record
        self._cached = False
        self._hierarchy_data = None

    @property
    def data(self):
        """Get the hierarchy data dictionary"""
        if not self._cached:
            self._ensure_hierarchy_data()
        return self._hierarchy_data

    def _ensure_hierarchy_data(self):
        """Ensure hierarchy data exists in the record"""
        if "hierarchy" not in self._record:
            self._record["hierarchy"] = {}
        self._hierarchy_data = self._record["hierarchy"]
        self._cached = True

    def get_children(self):
        """Get direct children of this record"""
        children_ids = self._get_direct_children(self._record.id)
        return [Vocabulary.get_record(child_id) for child_id in children_ids]

    def get_descendants(self):
        """Get all descendants (children, grandchildren, etc.) of this record"""
        descendants_ids = self._get_all_children(self._record.id)
        return [Vocabulary.get_record(desc_id) for desc_id in descendants_ids]

    def get_ancestors(self):
        """Get all ancestors of this record"""
        ancestors_ids = self._get_all_parents(self._record.id)
        return [Vocabulary.get_record(anc_id) for anc_id in ancestors_ids]

    def fix_hierarchy_on_self(self):
        """Fix hierarchy data on this record based on its parent"""
        parent = self._record.relations.parent()

        if not parent:
            self._record["hierarchy"] = {
                "level": 1,
                "titles": [self._record.get("title")]
                if self._record.get("title")
                else [],
                "ancestors": [],
                "ancestors_or_self": [self._record.get("id")],
                "leaf": not bool(self._get_direct_children(self._record.id)),
            }
        else:
            parent_hierarchy = parent["hierarchy"]

            self._record["hierarchy"] = {
                "level": parent_hierarchy["level"] + 1,
                "titles": [self._record.get("title")] + parent_hierarchy["titles"],
                "ancestors": parent_hierarchy["ancestors_or_self"],
                "ancestors_or_self": [self._record.get("id")]
                + parent_hierarchy["ancestors_or_self"],
                "leaf": not bool(self._get_direct_children(self._record.id)),
            }

        return self._record["hierarchy"]

    def fix_hierarchy_down(self):
        """Fix hierarchy for all descendants"""
        children_ids = self._get_all_children(self._record.id)

        # this is here due to circular import
        # and i need to access hierarchy field which is not available if i call get record on invenio Vocabulary
        from oarepo_vocabularies.records.api import Vocabulary as OarepoVocabulary

        for child_id in children_ids:
            child_record = OarepoVocabulary.get_record(child_id)
            child_hierarchy = child_record.hierarchy
            child_hierarchy.fix_hierarchy_on_self()
            child_record.commit()

    def update_parent_leaf_status(self):
        """Update leaf status for this record and its ancestors"""
        parent_rec = self._record.relations.parent()
        # current parent exists, change parent leaf if exists and if it is False
        if parent_rec is not None and parent_rec["hierarchy"]["leaf"]:
            parent_rec["hierarchy"]["leaf"] = False
            parent_rec.commit()
            return

        # update previous parent, if current parent is none
        if parent_rec is None and self._record._parent_cache.previous_uuid:
            previous_parent_rec = Vocabulary.get_record(
                self._record._parent_cache.previous_uuid
            )
            parent_has_children = bool(
                self._get_direct_children(self._record._parent_cache.previous_uuid)
            )

            if not previous_parent_rec["hierarchy"]["leaf"] and not parent_has_children:
                previous_parent_rec["hierarchy"]["leaf"] = True
                previous_parent_rec.commit()

    def _get_direct_children(self, parent_id=None):
        """Get direct children IDs"""
        if parent_id is None:
            parent_id = self._record.id

        result = (
            db.session.query(VocabularyHierarchy.id)
            .filter(VocabularyHierarchy.parent_id == parent_id)
            .all()
        )
        return [child_id for (child_id,) in result if child_id is not None]

    def _get_all_children(self, start_id=None):
        """Get all descendant IDs using recursive CTE"""
        # Base case: direct children of the node
        if start_id is None:
            start_id = self._record.id

        base = db.session.query(
            VocabularyHierarchy.id.label("id"), db.literal(1).label("depth")
        ).filter(VocabularyHierarchy.parent_id == start_id)

        # Recursive CTE
        hierarchy_cte = base.cte(name="children", recursive=True)
        child_alias = aliased(VocabularyHierarchy)

        recursive = db.session.query(
            child_alias.id, (hierarchy_cte.c.depth + 1).label("depth")
        ).filter(child_alias.parent_id == hierarchy_cte.c.id)

        hierarchy_cte = hierarchy_cte.union_all(recursive)

        # Final query with ORDER BY depth
        q = db.session.query(hierarchy_cte.c.id).order_by(hierarchy_cte.c.depth)
        return [cid for (cid,) in q.all() if cid is not None]

    def _get_all_parents(self, start_id=None):
        """Get all ancestor IDs using recursive CTE"""
        # Base case: direct parent of the node
        if start_id is None:
            start_id = self._record.id

        base = db.session.query(
            VocabularyHierarchy.parent_id.label("id"), db.literal(1).label("depth")
        ).filter(VocabularyHierarchy.id == start_id)

        # Recursive CTE
        hierarchy_cte = base.cte(name="parents", recursive=True)
        parent_alias = aliased(VocabularyHierarchy)

        recursive = db.session.query(
            parent_alias.parent_id, (hierarchy_cte.c.depth + 1).label("depth")
        ).filter(parent_alias.id == hierarchy_cte.c.id)

        hierarchy_cte = hierarchy_cte.union_all(recursive)

        # Final query with ORDER BY depth (closest parents first)
        q = db.session.query(hierarchy_cte.c.id).order_by(hierarchy_cte.c.depth)
        return [pid for (pid,) in q.all() if pid is not None]

    def __getitem__(self, key):
        """Allow dictionary-style access to hierarchy data"""
        if not self._cached:
            self._ensure_hierarchy_data()
        return self._hierarchy_data[key]

    def __setitem__(self, key, value):
        """Allow dictionary-style setting of hierarchy data"""
        if not self._cached:
            self._ensure_hierarchy_data()
        self._hierarchy_data[key] = value

    def __contains__(self, key):
        """Allow 'in' operator for hierarchy data"""
        if not self._cached:
            self._ensure_hierarchy_data()
        return key in self._hierarchy_data

    def get(self, key, default=None):
        """Get hierarchy data with default value"""
        if not self._cached:
            self._ensure_hierarchy_data()
        return self._hierarchy_data.get(key, default)

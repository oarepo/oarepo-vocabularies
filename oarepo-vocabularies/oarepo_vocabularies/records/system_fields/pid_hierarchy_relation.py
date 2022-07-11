from invenio_records.dictutils import dict_lookup, dict_set
from invenio_records.systemfields.relations import RelationResult
from invenio_records_resources.records.systemfields import PIDRelation
from invenio_db import db
import traceback


class RelationHierarchyResult(RelationResult):
    def dereference(self, keys=None, attrs=None):
        try:
            data = self._lookup_data()
            ret = self._dereference_one(
                data, keys or self.keys, attrs or self.attrs)
            dict_set(self.record, self.key, ret)
        except KeyError:
            return None

    def _dereference_one(self, data, keys, attrs):
        """Dereference a single object into a dict."""
        # Don't dereference if already referenced.
        if isinstance(data, list) and len(data) and '@v' in data[0]:
            return data

        # Get related record
        obj = self.resolve(data[self.field._value_key_suffix])
        # Inject selected key/values from related record into
        # the current record.

        return [self._dereference_one_hierarchy_level(d, keys, attrs) for d in obj.ancestors]

    def _dereference_one_hierarchy_level(self, obj, keys, attrs):
        if 'id' in obj:
            data = {
                'id': obj['id']
            }
        else:
            data = {}

        if keys is None:
            data.update({
                k: v for k, v in obj.items()
            })
        else:
            new_obj = {}
            for k in keys:
                try:
                    val = dict_lookup(obj, k)
                    if val:
                        dict_set(new_obj, k, val)
                except KeyError:
                    pass
            data.update(new_obj)

        # From record attributes (i.e. system fields)
        for a in attrs:
            data[a] = getattr(obj, a)

        # Add a version counter "@v" used for optimistic
        # concurrency control. It allows to search for all
        # outdated records and reindex them.
        data['@v'] = f'{obj.id}::{obj.revision_id}'
        return data


class PIDHierarchyRelation(PIDRelation):
    result_cls = RelationHierarchyResult

    def resolve(self, id_):
        """Resolve the value using the record class."""
        if id_ in self.cache:
            obj = self.cache[id_]
            return obj
        try:
            hierarchy = self.pid_field.resolve(id_)
            for obj in hierarchy.ancestors:
                db.session.expunge(obj.model)
            self.cache[id_] = hierarchy
            return hierarchy
            # TODO: there's many ways PID resolution can fail...
        except Exception:
            traceback.print_exc()
            return None

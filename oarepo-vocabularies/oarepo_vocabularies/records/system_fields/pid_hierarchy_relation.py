from invenio_records.dictutils import dict_lookup, dict_set
from invenio_records.systemfields.relations import RelationResult, ListRelation, InvalidCheckValue
from invenio_records_resources.records.systemfields import PIDRelation
from invenio_db import db
import traceback


class RelationHierarchyResultBase(RelationResult):
    multi = False

    def dereference(self, keys=None, attrs=None):
        try:
            data = self._lookup_data()
            ret = self._dereference_data(
                data, keys or self.keys, attrs or self.attrs)
            dict_set(self.record, self.key, ret)
        except KeyError:
            return None

    def _dereference_data(self, data, keys, attrs):

        # Don't dereference if already referenced.
        if isinstance(data, list) and len(data) and '@v' in data[0]:
            return data

        if not isinstance(data, (list, tuple)):
            data = [data]

        objects = [self.resolve(d[self.field._value_key_suffix]) for d in data]

        dereferenced = {}
        for obj in objects:
            for d in obj.ancestors:
                if d[self.field._value_key_suffix] in dereferenced:
                    break
                dereferenced[d[self.field._value_key_suffix]] = self._dereference_one_hierarchy_level(d, keys, attrs)

        dereferenced = list(dereferenced.values())
        dereferenced.sort(
            key=lambda x: (-len(x[self.field._value_key_suffix].split('/')), x[self.field._value_key_suffix]))
        return dereferenced

    def _dereference_one_hierarchy_level(self, obj, keys, attrs):
        if self.field._value_key_suffix in obj:
            data = {
                self.field._value_key_suffix: obj[self.field._value_key_suffix]
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

    def clean(self, keys=None, attrs=None):
        """Clean the dereferenced attributes inside the record."""
        try:
            data = self._lookup_data()
            return self._clean_data(
                data, keys or self.keys, attrs or self.attrs)
        except KeyError:
            return None

    def _clean_data(self, data, keys, attrs):
        """Remove all but "id" key for a dereferenced related object."""
        if data is None:
            return data
        if self.multi:
            if not isinstance(data, list):
                raise InvalidCheckValue(f'A list of vocabulary terms expected, got {type(data)}: {data}')
            for d in data:
                self._clean_one(d, keys, attrs)
            return data
        else:
            if not isinstance(data, dict):
                raise InvalidCheckValue(f'A single vocabulary term expected, got {data}')
            self._clean_one(data, keys, attrs)
            return data


class RelationHierarchyResult(RelationHierarchyResultBase):
    pass


class RelationHierarchyListResult(RelationHierarchyResultBase):
    multi = True


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


class PIDHierarchyListRelation(ListRelation, PIDHierarchyRelation):
    result_cls = RelationHierarchyListResult

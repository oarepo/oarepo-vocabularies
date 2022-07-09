"""Facet definitions."""

from elasticsearch_dsl import Facet
from elasticsearch_dsl.query import Nested
from invenio_records_resources.services.records.facets import TermsFacet


class NestedLabeledFacet(Facet):
    agg_type = "nested"

    def __init__(self, path, nested_facet, label=""):
        self._path = path
        self._inner = nested_facet
        self._label = label
        super(NestedLabeledFacet, self).__init__(
            path=path,
            aggs={
                "inner": nested_facet.get_aggregation(),
            },
        )

    def get_values(self, data, filter_values):
        return self._inner.get_values(data.inner, filter_values)

    def add_filter(self, filter_values):
        inner_q = self._inner.add_filter(filter_values)
        if inner_q:
            return Nested(path=self._path, query=inner_q)

    def get_labelled_values(self, data, filter_values):
        """Get a labelled version of a bucket."""
        try:
            out = data["buckets"]
        except:
            out = []
        return {"buckets": out, "label": str(self._label)}


uuid = TermsFacet(field="uuid")


indexed_at = TermsFacet(field="indexed_at")


created = TermsFacet(field="created")


updated = TermsFacet(field="updated")


type_pid_type = TermsFacet(field="type.pid_type")


type_id = TermsFacet(field="type.id")


pid_pk = TermsFacet(field="pid.pk")


pid_pid_type = TermsFacet(field="pid.pid_type")


pid_obj_type = TermsFacet(field="pid.obj_type")


pid_status = TermsFacet(field="pid.status")


title_sort = TermsFacet(field="title_sort")


icon = TermsFacet(field="icon")


hierarchy_level = TermsFacet(field="hierarchy.level")


_id = TermsFacet(field="id")


_schema = TermsFacet(field="$schema")

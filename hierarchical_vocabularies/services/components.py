from invenio_records_resources.services.records.components import ServiceComponent


class RelationsComponent(ServiceComponent):
    """Base service component."""

    def read(self, identity, record=None):
        """Read record handler."""
        record.relations.dereference()

    def read_draft(self, identity, draft=None):
        """Read draft handler."""
        draft.relations.dereference()


# class PIDHierarchyComponent(ServiceComponent):
#     def search(self, identity, search, params, **kwargs):
#         return super(PIDHierarchyComponent, self).search(
#             identity, search, params, **kwargs
#         )
#
#     def read(self, identity, **kwargs):
#         super(PIDHierarchyComponent, self).read(identity, **kwargs)
#         print("params from component read", kwargs)

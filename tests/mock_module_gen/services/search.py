from invenio_records_resources.services import SearchOptions as InvenioSearchOptions

from . import facets


def _(x):
    """Identity function for string extraction."""
    return x


class MockModuleGenSearchOptions(InvenioSearchOptions):
    """MockModuleGenRecord search options."""

    facets = {
        "hierarchy_id": facets.hierarchy_id,
        "_id": facets._id,
        "created": facets.created,
        "updated": facets.updated,
        "_schema": facets._schema,
        "hlist_id": facets.hlist_id,
        "hlist": facets.hlist,
    }
    sort_options = {
        **InvenioSearchOptions.sort_options,
    }

from invenio_records_resources.services import SearchOptions as InvenioSearchOptions

from . import facets


def _(x):
    """Identity function for string extraction."""
    return x


from oarepo_vocabularies.services.search import OARepoVocabulariesSearchOptionsBase


class OARepoVocabulariesBasicSearchOptions(
    OARepoVocabulariesSearchOptionsBase, InvenioSearchOptions
):
    """OARepoVocabularyBasic search options."""

    facets = {
        "uuid": facets.uuid,
        "indexed_at": facets.indexed_at,
        "created": facets.created,
        "updated": facets.updated,
        "type_pid_type": facets.type_pid_type,
        "type_id": facets.type_id,
        "pid_pk": facets.pid_pk,
        "pid_pid_type": facets.pid_pid_type,
        "pid_obj_type": facets.pid_obj_type,
        "pid_status": facets.pid_status,
        "title_sort": facets.title_sort,
        "icon": facets.icon,
        "hierarchy_level": facets.hierarchy_level,
        "_id": facets._id,
        "_schema": facets._schema,
    }
    sort_options = {
        **OARepoVocabulariesSearchOptionsBase.sort_options,
    }

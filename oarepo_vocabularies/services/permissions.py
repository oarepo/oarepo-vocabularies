from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_vocabularies.services.permissions import PermissionPolicy

class VocabulariesPermissionPolicy(PermissionPolicy):
    # NOTE: probably change to an authenticated user later.
    can_list_vocabularies = [SystemProcess(), AnyUser()]
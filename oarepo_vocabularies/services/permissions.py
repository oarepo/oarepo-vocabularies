from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_permissions.policies.base import BasePermissionPolicy


class VocabulariesPermissionPolicy(BasePermissionPolicy):
    # NOTE: probably change to an authenticated user later.
    can_list_vocabularies = [SystemProcess(), AnyUser()]

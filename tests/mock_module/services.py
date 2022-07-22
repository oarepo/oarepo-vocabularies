from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import SystemProcess, AnyUser
from invenio_records_resources.services import RecordService, RecordServiceConfig
from invenio_records_resources.services.records.components import DataComponent, MetadataComponent, RelationsComponent

from tests.mock_module.api import Record
from tests.mock_module.schema import MockSchema


class MockServicePermission(RecordPermissionPolicy):
    can_create = [SystemProcess()]
    can_read = [AnyUser(), SystemProcess()]


class MockServiceConfig(RecordServiceConfig):
    record_cls = Record
    schema = MockSchema
    permission_policy_cls = MockServicePermission
    components = [
        MetadataComponent,
        DataComponent,
        RelationsComponent
    ]


class MockService(RecordService):
    pass

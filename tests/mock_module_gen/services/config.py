from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from invenio_records_resources.services.records.components import (
    DataComponent,
    RelationsComponent,
)
from mock_module_gen.records.api import MockModuleGenRecord
from mock_module_gen.services.permissions import MockModuleGenPermissionPolicy
from mock_module_gen.services.schema import MockModuleGenSchema
from mock_module_gen.services.search import MockModuleGenSearchOptions


class MockModuleGenServiceConfig(InvenioRecordServiceConfig):
    """MockModuleGenRecord service config."""

    permission_policy_cls = MockModuleGenPermissionPolicy
    schema = MockModuleGenSchema
    search = MockModuleGenSearchOptions
    record_cls = MockModuleGenRecord

    components = [
        *InvenioRecordServiceConfig.components,
        DataComponent,
        RelationsComponent,
    ]

    model = "mock_module_gen"

    @property
    def links_item(self):
        return {
            "self": RecordLink("/mock_module_gen/{id}"),
        }

    links_search = pagination_links("/mock_module_gen/{?args*}")

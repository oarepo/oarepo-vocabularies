from invenio_records_resources.resources import (
    RecordResourceConfig as InvenioRecordResourceConfig,
)


class MockModuleGenResourceConfig(InvenioRecordResourceConfig):
    """MockModuleGenRecord resource config."""

    blueprint_name = "MockModuleGen"
    url_prefix = "/mock_module_gen/"

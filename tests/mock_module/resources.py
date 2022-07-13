from flask import Blueprint
from invenio_records_resources.resources import RecordResourceConfig, RecordResource


class MockResourceConfig(RecordResourceConfig):
    url_prefix = '/<match(path="vocabularies"):pth>/record'
    blueprint_name = "mock_record"


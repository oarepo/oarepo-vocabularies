from flask import g
from flask_resources import from_conf, request_parser
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from oarepo_ui.resources.resource import RecordsUIResource

request_vocabulary_args = request_parser(
    from_conf("request_vocabulary_type_args"), location="view_args"
)


class InvenioVocabulariesUIResource(RecordsUIResource):
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def detail(self):
        return super().detail()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def export(self):
        return super().export()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def search(self):
        return super().search()

    def _get_record(self, resource_requestctx):
        return self._api_service.read(
            g.identity,
            (
                resource_requestctx.view_args["vocabulary_type"],
                resource_requestctx.view_args["pid_value"],
            ),
        )

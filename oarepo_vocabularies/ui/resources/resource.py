from flask import g
from flask_resources import from_conf, request_parser, resource_requestctx
from flask_security import login_required
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from invenio_records_resources.services import LinksTemplate
from oarepo_ui.proxies import current_oarepo_ui
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

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def create(self):
        return super().create()

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def edit(self):
        return super().edit()

    def _get_record(self, resourcerequestctx, allow_draft=False, include_deleted=False):
        pid_value = resource_requestctx.view_args["pid_value"]
        vocabulary_type = resource_requestctx.view_args["vocabulary_type"]
        return self.api_service.read(
            g.identity,
            (
                vocabulary_type,
                pid_value,
            ),
        )

    def empty_record(self, resource_requestctx, **kwargs):
        record = super().empty_record(resource_requestctx=resource_requestctx)
        if "metadata" in record:
            del record["metadata"]
        record["type"] = resource_requestctx.view_args["vocabulary_type"]
        record["tags"] = []
        return record

    def expand_detail_links(self, identity, record):
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item,
            {
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": resource_requestctx.view_args["vocabulary_type"],
            },
        )
        return tpl.expand(identity, record)

    def expand_search_links(self, identity, pagination, args):
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_search,
            {
                "config": self.config,
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": resource_requestctx.view_args["vocabulary_type"],
                "args": args,
            },
        )
        return tpl.expand(identity, pagination)

    def vocabulary_type_does_not_exist(self, error, *args, **kwargs):
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "no_vocabulary_type",
                identity=g.identity,
                default_macro="NoVocabularyType",
            ),
            message=str(error),
        )

    def _exportable_handlers(self):
        """Get the list of exportable handlers.

        returns: list of exportable handlers (mimetype, handler)
        """
        return []

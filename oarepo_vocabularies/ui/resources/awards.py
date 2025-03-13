import marshmallow as ma
from flask import current_app
from invenio_records_resources.services import Link, pagination_links
from oarepo_ui.resources.components import PermissionsComponent
from oarepo_ui.resources.config import RecordsUIResourceConfig
from oarepo_ui.resources.links import UIRecordLink

from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from oarepo_vocabularies.ui.resources.components.search import VocabularySearchComponent
from oarepo_vocabularies.ui.resources.components.vocabulary_ui_resource import (
    VocabularyRecordsComponent,
)
from oarepo_ui.resources.components.custom_fields import CustomFieldsComponent


from .config import InvenioVocabulariesUIResourceConfig
from .resource import InvenioVocabulariesUIResource
from flask import g
from flask_resources import from_conf, request_parser, resource_requestctx
from flask_security import login_required
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from invenio_records_resources.services import LinksTemplate
from oarepo_ui.resources.resource import RecordsUIResource


class InvenioVocabulariesAwardsUIResource(InvenioVocabulariesUIResource):
    @request_read_args
    @request_view_args
    def detail(self):
        resource_requestctx.view_args["vocabulary_type"] = "awards"
        return super().detail()

    @request_read_args
    @request_view_args
    def export(self):
        resource_requestctx.view_args["vocabulary_type"] = "awards"
        return super().export()

    @request_read_args
    @request_view_args
    def search(self):
        resource_requestctx.view_args["vocabulary_type"] = "awards"
        try:
            return super().search()
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise e

    @login_required
    @request_read_args
    @request_view_args
    def create(self):
        resource_requestctx.view_args["vocabulary_type"] = "awards"
        return super().create()

    @login_required
    @request_read_args
    @request_view_args
    def edit(self):
        resource_requestctx.view_args["vocabulary_type"] = "awards"
        return super().edit()

    def _get_record(self, resource_requestctx, allow_draft=False):
        return self.api_service.read(
            g.identity,
            (
                "awards",
                resource_requestctx.view_args["pid_value"],
            ),
        )

    def empty_record(self, resource_requestctx, **kwargs):
        record = super().empty_record(resource_requestctx=resource_requestctx)
        if "metadata" in record:
            del record["metadata"]
        record["type"] = "awards"
        record["tags"] = []
        return record

    def _get_record(self, resource_requestctx, allow_draft=False):
        return self.api_service.read(
            g.identity,
            resource_requestctx.view_args["pid_value"],
        )

    def expand_detail_links(self, identity, record):
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item,
            {
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": "awards",
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
                "vocabulary_type": "awards",
                "args": args,
            },
        )
        return tpl.expand(identity, pagination)


class InvenioVocabulariesAwardsUIResourceConfig(InvenioVocabulariesUIResourceConfig):
    template_folder = "../templates"
    url_prefix = "/vocabularies/awards/"
    blueprint_name = "oarepo_vocabularies_awards_ui"
    api_service = "awards"
    application_id = "OarepoVocabulariesAwards"

    routes = {
        "create": "/_new",
        "edit": "/<pid_value>/edit",
        "search": "/",
        "detail": "/<pid_value>",
        "export": "/<pid_value>/export/<export_format>",
    }
    config_routes = {
        "form_config": "/form",
    }

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return "/api/awards"

    request_vocabulary_type_args = {}
    request_form_config_view_args = {}

    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}/{id}"),
        "edit": UIRecordLink("{+ui}{+url_prefix}/{id}/edit"),
        "search": UIRecordLink("{+ui}{+url_prefix}/"),
        "create": UIRecordLink("{+ui}{+url_prefix}/_new"),
    }

    @property
    def ui_links_search(self):
        return {
            **pagination_links("{+ui}{+url_prefix}/{?args*}"),
            "create": Link("{+ui}{+url_prefix}/_new"),
        }

    def vocabulary_props_config(self, vocabulary_type):
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(
            vocabulary_type, {}
        )

    def _get_custom_fields_ui_config(self, key, view_args=None, **kwargs):
        if key == "OAREPO_VOCABULARIES_HIERARCHY_CF":
            return []
        return current_app.config.get("VOCABULARIES_CF_UI", {}).get("awards", [])

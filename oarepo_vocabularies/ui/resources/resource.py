#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource for vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g
from flask_resources import from_conf, request_parser, resource_requestctx
from flask_security import login_required
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from invenio_records_resources.services import LinksTemplate
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources.records.resource import RecordsUIResource

if TYPE_CHECKING:
    from typing import Any

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services.records.results import RecordItem
    from werkzeug import Response

request_vocabulary_args = request_parser(from_conf("request_vocabulary_type_args"), location="view_args")


class InvenioVocabulariesUIResource(RecordsUIResource):
    """Invenio Vocabularies UI Resource."""

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def detail(self) -> Response:
        """Return item detail page."""
        return super().detail()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def export(self) -> tuple[Any, int, dict[str, str]]:
        """Export a record in the specified format."""
        return super().export()

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def search(self) -> str | Response:
        """Return search page."""
        return super().search()

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def create(self) -> str | Response:
        """Return create page for a record."""
        return super().create()

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def edit(self) -> str | Response:
        """Return edit page for a record."""
        return super().edit()

    def _get_record(
        self,
        resourcerequestctx: Any,  # noqa: ARG002
        allow_draft: bool = False,  # noqa: ARG002
        include_deleted: bool = False,  # noqa: ARG002
    ) -> RecordItem:
        """Get a record from the service."""
        pid_value = resource_requestctx.view_args["pid_value"]
        vocabulary_type = resource_requestctx.view_args["vocabulary_type"]
        return self.api_service.read(
            g.identity,
            (
                vocabulary_type,
                pid_value,
            ),
        )

    def empty_record(self, resource_requestctx: Any) -> Record:
        """Create an empty record with type and tags initialized."""
        record = super().empty_record(resource_requestctx=resource_requestctx)
        if "metadata" in record:
            del record["metadata"]
        record["type"] = resource_requestctx.view_args["vocabulary_type"]
        record["tags"] = []
        return record

    def expand_detail_links(self, identity: Identity, record: Record) -> dict:
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item,
            {
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": resource_requestctx.view_args["vocabulary_type"],
            },
        )
        return tpl.expand(identity, record)

    def expand_search_links(self, identity: Identity, pagination: Any, args: Any) -> dict:
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

    def vocabulary_type_does_not_exist(self, error) -> str:  # noqa: ANN001
        """Render vocabulary type does not exist page."""
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "no_vocabulary_type",
                identity=g.identity,
                default_macro="NoVocabularyType",
            ),
            message=str(error),
        )

    def _exportable_handlers(self) -> list:
        """Get the list of exportable handlers.

        returns: list of exportable handlers (mimetype, handler)
        """
        return []

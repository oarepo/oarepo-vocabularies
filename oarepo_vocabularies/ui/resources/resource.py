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
    from invenio_records_resources.pagination import Pagination
    from invenio_records_resources.services.records.results import RecordItem
    from werkzeug import Response

request_vocabulary_args = request_parser(from_conf("request_vocabulary_type_args"), location="view_args")


class InvenioVocabulariesUIResource(RecordsUIResource):
    """Invenio Vocabularies UI Resource."""

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def detail(self, pid_value: str, embed: bool = False, is_preview: bool = False, **kwargs: Any) -> Response:
        """Return item detail page."""
        return super().detail(pid_value=pid_value, embed=embed, is_preview=is_preview, **kwargs)

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def export(
        self,
        pid_value: str,
        export_format: str,
        **kwargs: Any,
    ) -> Any:
        """Export a record in the specified format."""
        return super().export(pid_value=pid_value, export_format=export_format, **kwargs)

    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def search(self, page: int = 1, size: int = 10, **kwargs: Any) -> str | Response:
        """Return search page."""
        return super().search(page=page, size=size, **kwargs)

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def create(self, **kwargs: Any) -> str | Response:
        """Return create page for a record."""
        return super().create(**kwargs)

    @login_required
    @request_read_args
    @request_view_args
    @request_vocabulary_args
    def edit(self, pid_value: str, **kwargs: Any) -> str | Response:
        """Return edit page for a record."""
        return super().edit(pid_value=pid_value, **kwargs)

    def _get_record(self, pid_value: str, allow_draft: bool = False, include_deleted: bool = False) -> RecordItem:  # noqa: ARG002
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

    def empty_record(self, **kwargs: Any) -> dict[str, Any]:
        """Create an empty record with type and tags initialized."""
        record: dict[str, Any] = super().empty_record(**kwargs)
        record.pop("metadata", None)
        record["type"] = kwargs.get("vocabulary_type")
        record["tags"] = []
        return record

    def expand_detail_links(self, identity: Identity, record: RecordItem) -> Any:
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item,
            {
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": resource_requestctx.view_args["vocabulary_type"],
            },
        )
        return tpl.expand(identity, record)

    def expand_search_links(self, identity: Identity, pagination: Pagination, query_args: dict[str, str]) -> Any:
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_search,
            {
                "config": self.config,
                "url_prefix": self.config.url_prefix,
                "vocabulary_type": resource_requestctx.view_args["vocabulary_type"],
                "args": query_args,
            },
        )
        return tpl.expand(identity, pagination)

    def vocabulary_type_does_not_exist(self, error) -> Any:  # noqa: ANN001
        """Render vocabulary type does not exist page."""
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "no_vocabulary_type",
                identity=g.identity,  # type: ignore[attr-defined]
                default_macro="NoVocabularyType",
            ),
            message=str(error),
        )

    def _exportable_handlers(self) -> list:
        """Get the list of exportable handlers.

        returns: list of exportable handlers (mimetype, handler)
        """
        return []

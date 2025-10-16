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
from flask_resources import from_conf, request_parser
from invenio_records_resources.services import LinksTemplate
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources.base import pass_route_args
from oarepo_ui.resources.records.resource import RecordsUIResource

if TYPE_CHECKING:
    from typing import Any

    from flask_principal import Identity
    from invenio_records_resources.pagination import Pagination
    from invenio_records_resources.services.records.results import RecordItem

request_vocabulary_args = request_parser(from_conf("request_type_args"), location="view_args")


# TODO: will be removed in favour of administration view
class InvenioVocabulariesUIResource(RecordsUIResource):
    """Invenio Vocabularies UI Resource."""

    @pass_route_args("vocabulary_type")
    def search(self, *args: Any, **kwargs: Any) -> Any:
        """Search records."""
        super().search(*args, **kwargs)

    def _get_record(  # type: ignore[override]
        self,
        pid_value: str,
        type_: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> RecordItem:
        """Get a record from the service."""
        if not type_:
            raise ValueError("Vocabulary type is required to get a record.")

        return self.api_service.read(
            g.identity,
            (
                type_,  # type: ignore[arg-type]
                pid_value,
            ),
        )

    def empty_record(self, **kwargs: Any) -> dict[str, Any]:
        """Create an empty record with type and tags initialized."""
        record: dict[str, Any] = super().empty_record(**kwargs)
        record.pop("metadata", None)
        record["type"] = kwargs.get("type")
        record["tags"] = []
        return record

    def expand_detail_links(self, identity: Identity, record: RecordItem) -> Any:
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item,
            {
                "url_prefix": self.config.url_prefix,
                "type": record.data["type"],
            },
        )
        return tpl.expand(identity, record)

    def expand_search_links(self, identity: Identity, pagination: Pagination, query_args: dict[str, str]) -> Any:
        """Get links for this result item."""
        # copy the original query args as we are going to modify them
        query_args_copied = query_args.copy()
        type_ = query_args_copied.pop("type_")

        tpl = LinksTemplate(
            self.config.ui_links_search,
            {
                "config": self.config,
                "url_prefix": self.config.url_prefix,
                "type": type_,
                "args": query_args_copied,
            },
        )
        return tpl.expand(identity, pagination)

    def vocabulary_type_does_not_exist(self, error) -> Any:  # noqa: ANN001
        """Render vocabulary type does not exist page."""
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "no_vocabulary_type",
                default_macro="NoVocabularyType",
            ),
            message=str(error),
        )

    def _exportable_handlers(self) -> list:
        """Get the list of exportable handlers.

        returns: list of exportable handlers (mimetype, handler)
        """
        return []

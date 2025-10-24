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

from functools import partial
from typing import TYPE_CHECKING

from flask import g
from flask_resources import from_conf, request_parser
from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.base.links import (
    EndpointLink,
)
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources.base import pass_route_args
from oarepo_ui.resources.records.resource import RecordsUIResource
from oarepo_ui.templating.data import FieldData
from werkzeug import Response

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
        return super().search(*args, **kwargs)

    @pass_route_args("vocabulary_type")
    def deposit_create(self, *args: Any, **kwargs: Any) -> Any:
        """Create a new deposit."""
        return super().deposit_create(*args, **kwargs)

    @pass_route_args("vocabulary_type")
    @pass_route_args("view")
    def record_detail(self, *args: Any, **kwargs: Any) -> Any:
        """Record detail view."""
        api_record = self._get_record(kwargs["pid_value"], kwargs["type"])

        render_method = self.get_jinjax_macro(
            "record_detail",
        )
        dict_record = api_record.to_dict()
        record_ui = self.config.ui_serializer.dump_obj(dict_record)
        record_ui.setdefault("links", {})
        vocabulary_type = kwargs["type"]
        extra_context = {}
        extra_context["vocabularyType"] = vocabulary_type

        self.run_components(
            "before_ui_detail",
            api_record=api_record,
            record=api_record.to_dict(),
            identity=g.identity,
            extra_context=extra_context,
            ui_links={},
        )

        search_options = dict(
            api_config=self.api_service.config,
            identity=g.identity,
            endpoint=EndpointLink("vocabularies.search", params=["type"]).expand(
                {},
                {"type": vocabulary_type},
            ),
            initial_filters=[["h-parent", api_record["id"]]],
            overrides={"type": vocabulary_type},
        )
        search_config = partial(self.config.search_app_config, **search_options)
        extra_context.setdefault("search_app_config", search_config)
        extra_context["vocabularyType"] = vocabulary_type
        extra_context["vocabularyProps"] = self.config.vocabulary_props_config(vocabulary_type)
        render_kwargs = {
            "record": api_record,
            "record_ui": record_ui,
            # TODO: implement user_communities_memberships
            "permissions": api_record.has_permissions_to(
                [
                    "edit",
                    "new_version",
                    "manage",
                    "update_draft",
                    "read_files",
                    "review",
                    "view",
                    "media_read_files",
                    "moderate",
                ]
            ),
            "extra_context": extra_context,
            "context": current_oarepo_ui.catalog.jinja_env.globals,
            "d": FieldData.create(
                api_data=api_record.to_dict(),
                ui_data=record_ui,
                ui_definitions=self.ui_model,
                item_getter=self.config.field_data_item_getter,
            ),
        }
        response = Response(
            current_oarepo_ui.catalog.render(
                render_method,
                **render_kwargs,
            ),
            mimetype="text/html",
            status=200,
        )
        response._api_record = api_record
        return response

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
        type = query_args_copied.pop("type")  # NoQA: A001

        tpl = LinksTemplate(
            self.config.ui_links_search,
            {
                "config": self.config,
                "url_prefix": self.config.url_prefix,
                "type": type,
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

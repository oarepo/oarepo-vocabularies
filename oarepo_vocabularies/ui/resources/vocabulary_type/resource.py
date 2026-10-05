# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Vocabulary Type UI Resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from flask import current_app, g
from flask_resources import route
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import RecordsUIResourceConfig, UIResource

if TYPE_CHECKING:
    import builtins

    from flask_resources import ResourceConfig

    from oarepo_vocabularies.services.service import VocabularyTypeService


class VocabularyTypeUIResource(UIResource):
    """Vocabulary Type UI Resource."""

    config: RecordsUIResourceConfig

    def __init__(self, config: ResourceConfig, service: VocabularyTypeService) -> None:
        """Initialize the VocabularyTypeUIResource."""
        super().__init__(config)
        self.service = service

    @override
    def create_url_rules(self) -> builtins.list[dict[str, Any]]:
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        list_route = routes["list"]
        if not list_route.endswith("/"):
            list_route += "/"
        list_route_without_slash = list_route[:-1]
        return [
            route("GET", list_route, self.list),
            route(
                "GET",
                list_route_without_slash,
                self.list,
                endpoint="list-route-without-slash",
            ),
        ]

    def list(self) -> Any:
        """Return vocabulary types page."""
        list_data = self.service.search(g.identity).to_dict()

        config_metadata = current_app.config["INVENIO_VOCABULARY_TYPE_METADATA"]
        for item in list_data["hits"]["hits"]:
            for id_ in config_metadata:
                if item["id"] == id_:
                    for key, value in config_metadata[id_].items():
                        item[key] = value

        # TODO: handle permissions UI way - better response than generic error
        serialized_list_data = self.config.ui_serializer.dump_list(list_data)

        extra_context: dict = {}
        self.run_components(
            "before_ui_list",
            resource=self,
            list_data=serialized_list_data,
            identity=g.identity,
            extra_context=extra_context,
            ui_config=self.config,
            ui_resource=self,
            component_key="list",
        )

        _catalog = current_oarepo_ui.catalog

        return _catalog.render(
            cast("str", self.config.templates["list"]),
            list_data=serialized_list_data,
        )

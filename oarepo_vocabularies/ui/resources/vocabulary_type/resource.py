#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabulary Type UI Resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flask import current_app, g
from flask_resources import route
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import UIResource

from oarepo_vocabularies.proxies import current_oarepo_vocabularies

if TYPE_CHECKING:
    from flask_resources import ResourceConfig
    from invenio_records_resources.services.base.service import Service


class VocabularyTypeUIResource(UIResource):
    """Vocabulary Type UI Resource."""

    def __init__(self, config: ResourceConfig, service: Service) -> None:
        """Initialize the VocabularyTypeUIResource."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self) -> list:
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

        for specialized_service_type in current_app.config.get("OAREPO_VOCABULARIES_SPECIALIZED_SERVICES", {}).values():
            specialized_service = current_oarepo_vocabularies.get_specialized_service(specialized_service_type)

            specialized_vocabulary_data = {}
            if specialized_service is not None:
                specialized_vocabulary_data = specialized_service.search(g.identity).to_dict()

            if specialized_vocabulary_data:
                list_data["hits"]["hits"].append(
                    {
                        "count": specialized_vocabulary_data["hits"]["total"],
                        "self_html": f"/vocabularies/{specialized_service_type}",
                        "id": specialized_service_type,
                        "name": current_app.config.get("OAREPO_SPECIALIZED_VOCABULARIES_METADATA", {})
                        .get(specialized_service_type, {})
                        .get("name", {}),
                        "description": current_app.config.get("OAREPO_SPECIALIZED_VOCABULARIES_METADATA", {})
                        .get(specialized_service_type, {})
                        .get("description", {}),
                    }
                )

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
            self.config.templates["list"],
            list_data=serialized_list_data,
        )

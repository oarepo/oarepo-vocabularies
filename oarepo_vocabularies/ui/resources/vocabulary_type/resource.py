from flask import current_app, g
from flask_resources import route
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import UIResource
from oarepo_vocabularies.proxies import current_oarepo_vocabularies


class VocabularyTypeUIResource(UIResource):
    def __init__(self, config, service):
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
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

    def list(self):
        """Returns vocabulary types page."""
        list_data = self.service.search(g.identity).to_dict()

        for specialized_service_type in current_app.config.get(
            "OAREPO_VOCABULARIES_SPECIALIZED_SERVICES", {}
        ).values():
            specialized_service = current_oarepo_vocabularies.get_specialized_service(
                specialized_service_type
            )

            specialized_vocabulary_data = specialized_service.search(
                g.identity
            ).to_dict()

            list_data["hits"]["hits"].append(
                {
                    "count": specialized_vocabulary_data["hits"]["total"],
                    "self_html": f"/vocabularies/{specialized_service_type}",
                    "id": specialized_service_type,
                    "name": current_app.config.get(
                        "OAREPO_SPECIALIZED_VOCABULARIES_METADATA", {}
                    )
                    .get(specialized_service_type, {})
                    .get("name", {}),
                    "description": current_app.config.get(
                        "OAREPO_SPECIALIZED_VOCABULARIES_METADATA", {}
                    )
                    .get(specialized_service_type, {})
                    .get("description", {}),
                }
            )

        config_metadata = current_app.config["INVENIO_VOCABULARY_TYPE_METADATA"]
        for item in list_data["hits"]["hits"]:
            for id in config_metadata.keys():
                if item["id"] == id:
                    for key, value in config_metadata[id].items():
                        item[key] = value

        # TODO: handle permissions UI way - better response than generic error
        serialized_list_data = self.config.ui_serializer.dump_list(list_data)

        extra_context = dict()
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

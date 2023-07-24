from flask import current_app, g, redirect, render_template, request
from flask_resources import route
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import UIResource


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
            route("GET", list_route_without_slash, self.list_without_slash),
        ]

    def list(self):
        """Returns vocabulary types page."""
        # record = self._get_record(resource_requestctx)
        list_data = self.service.search(g.identity).to_dict()

        config_metadata = current_app.config["INVENIO_VOCABULARY_TYPE_METADATA"]
        for item in list_data["hits"]["hits"]:
            for id in config_metadata.keys():
                if item["id"] == id:
                    for key, value in config_metadata[id].items():
                        item[key] = value

        # TODO: handle permissions UI way - better response than generic error
        serialized_list_data = self.config.ui_serializer.dump_list(list_data)

        # make links absolute
        # if "links" in serialized_list_data:
        #     for k, v in list(serialized_record["links"].items()):
        #         if not isinstance(v, str):
        #             continue
        #         if not v.startswith("/") and not v.startswith("https://"):
        #             v = f"/api{self.api_service.config.url_prefix}{v}"
        #             serialized_record["links"][k] = v

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

        template_def = self.config.templates["list"]
        template = current_oarepo_ui.get_template(template_def["layout"], {})

        return render_template(
            template,
            list_data=serialized_list_data,
            ui_config=self.config,
            ui_resource=self,
            component_key="list",
            **extra_context,
        )

    def list_without_slash(self):
        split_path = request.full_path.split("?", maxsplit=1)
        path_with_slash = split_path[0] + "/"
        if len(split_path) == 1:
            return redirect(path_with_slash, code=302)
        else:
            return redirect(path_with_slash + "?" + split_path[1], code=302)

from functools import partial

from invenio_records_resources.services.records.components import ServiceComponent


class VocabularyRecordsComponent(ServiceComponent):
    """
    This component is used for UI search & display of a vocabulary item
    """

    def before_ui_search(self, *, resource, search_options, view_args, **kwargs):
        vocabulary_type = view_args["vocabulary_type"]
        api_service = resource.api_service
        search_options.setdefault(
            "endpoint",
            api_service.config.links_search["self"].expand(
                None, {"type": vocabulary_type, "api": "/api"}
            ),
        )

    def before_ui_detail(
        self, *, extra_context, resource, identity, view_args, record, **kwargs
    ):
        vocabulary_type = view_args["vocabulary_type"]
        api_service = resource.api_service
        search_options = dict(
            api_config=api_service.config,
            identity=identity,
            endpoint=api_service.config.links_search["self"].expand(
                None, {"type": vocabulary_type, "api": "/api"}
            ),
            initial_filters=[["h-parent", record["id"]]],
        )
        search_config = partial(resource.config.search_app_config, **search_options)
        extra_context.setdefault("search_app_config", search_config)
        extra_context["vocabularyProps"] = resource.config.vocabulary_props_config(
            vocabulary_type
        )

    def before_ui_edit(self, *, form_config, resource, record, view_args, **kwargs):
        vocabulary_type = view_args["vocabulary_type"]
        form_config.setdefault(
            "vocabularyProps", resource.config.vocabulary_props_config(vocabulary_type)
        )
        form_config.setdefault(
            "updateUrl",
            record["links"].get("self", None),
        )

    def before_ui_create(self, *, form_config, resource, view_args, **kwargs):
        vocabulary_type = view_args["vocabulary_type"]
        api_service = resource.api_service
        form_config.setdefault(
            "vocabularyProps", resource.config.vocabulary_props_config(vocabulary_type)
        )
        form_config[
            "createUrl"
        ] = f"/api{api_service.config.url_prefix}{vocabulary_type}"

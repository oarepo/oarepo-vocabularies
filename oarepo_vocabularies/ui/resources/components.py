from invenio_records_resources.services.records.components import ServiceComponent


class VocabulariesSearchComponent(ServiceComponent):
    def before_ui_search(self, *, resource, search_options, view_args, **kwargs):
        vocabulary_type = view_args["vocabulary_type"]
        api_service = resource._api_service
        search_options.setdefault(
            "endpoint",
            api_service.config.links_search["self"].expand(
                None, {"type": vocabulary_type, "api": "/api"}
            ),
        )

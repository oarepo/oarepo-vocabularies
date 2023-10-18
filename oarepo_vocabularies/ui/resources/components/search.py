from invenio_records_resources.services.records.components import ServiceComponent


class VocabularySearchComponent(ServiceComponent):
    def before_ui_search(self, *, resource, search_options, view_args, **kwargs):
        search_options["headers"] = {"Accept": "application/json"}

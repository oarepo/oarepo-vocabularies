from oarepo_ui.resources.components import UIResourceComponent


class VocabularySearchComponent(UIResourceComponent):
    def before_ui_search(self, *, search_options, view_args, **kwargs):
        search_options["headers"] = {"Accept": "application/json"}

from functools import partial
from flask import current_app
from invenio_i18n.ext import current_i18n

from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow_utils.fields.babel import gettext_from_dict
from oarepo_ui.proxies import current_oarepo_ui


class DepositVocabularyOptionsComponent(ServiceComponent):
    def form_config(self, *, form_config, resource, record, view_args, identity, **kwargs):
        form_config.setdefault("vocabularies", {})

        if current_app.config.get("VOCABULARIES_LANGUAGES_DISABLED"):
            return

        languages = vocabulary_service.read_all(
            identity, fields=["id", "title"], type="languages", max_records=500
        )

        language_options = []

        for hit in languages.to_dict()["hits"]["hits"]:
            code = hit["id"]
            label = gettext_from_dict(
                hit["title"],
                current_i18n.locale,
                current_app.config.get("BABEL_DEFAULT_LOCALE", "en"),
            )
            option = dict(text=label or code, value=code)

            language_options.append(option)

        form_config["vocabularies"]["languages"] = language_options


class VocabularyRecordsComponent(ServiceComponent):
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



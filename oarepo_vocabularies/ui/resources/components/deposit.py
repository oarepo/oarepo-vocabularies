from flask import current_app
from invenio_i18n.ext import current_i18n
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow_utils.fields.babel import gettext_from_dict


class DepositVocabularyOptionsComponent(ServiceComponent):
    """
    This component is used for deposition of a vocabulary item. It provides
    a list of languages so that title & description can have the languages
    pre-filled
    """

    def form_config(
        self, *, form_config, resource, record, view_args, identity, **kwargs
    ):
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

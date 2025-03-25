import marshmallow as ma
from flask import current_app
from invenio_records_resources.services import Link, pagination_links
from oarepo_ui.resources.components import PermissionsComponent
from oarepo_ui.resources.config import RecordsUIResourceConfig
from oarepo_ui.resources.links import UIRecordLink

from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from oarepo_vocabularies.ui.resources.components.search import VocabularySearchComponent
from oarepo_vocabularies.ui.resources.components.vocabulary_ui_resource import (
    VocabularyRecordsComponent,
)
from oarepo_ui.resources.components.custom_fields import CustomFieldsComponent

from invenio_vocabularies.records.models import VocabularyType

from oarepo_vocabularies.errors import VocabularyTypeDoesNotExist


class VocabularyFormDepositVocabularyOptionsComponent(
    DepositVocabularyOptionsComponent
):
    always_included_vocabularies = ["languages"]

    def form_config(self, *, form_config, **kwargs):
        super().form_config(form_config=form_config, **kwargs)

        if "languages" not in form_config["vocabularies"]:
            form_config["vocabularies"]["languages"] = []

        if not form_config["vocabularies"]["languages"]:
            form_config["vocabularies"]["languages"] = [
                {"text": "English", "value": "en"}
            ]


class VocabularyTypeValidationSchema(ma.Schema):
    vocabulary_type = ma.fields.String()

    def load(self, data, *args, **kwargs):
        vocabulary_type = data.get("vocabulary_type")
        # TODO: this will not be needed once specialized vocabs get their own resource
        allowed_specialized_vocabularies = current_app.config.get(
            "OAREPO_VOCABULARIES_SPECIALIZED_SERVICES", []
        )

        try:
            if (
                VocabularyType.query.filter_by(id=vocabulary_type).one_or_none()
                or vocabulary_type in allowed_specialized_vocabularies.values()
            ):
                return {"vocabulary_type": vocabulary_type}
            else:
                raise VocabularyTypeDoesNotExist(
                    f"Vocabulary type {vocabulary_type} does not exist."
                )

        except VocabularyTypeDoesNotExist as e:
            raise e
        except Exception:
            raise VocabularyTypeDoesNotExist(
                f"Vocabulary type {vocabulary_type} does not exist."
            )


class InvenioVocabulariesUIResourceConfig(RecordsUIResourceConfig):
    template_folder = "../templates"
    url_prefix = "/vocabularies/"
    blueprint_name = "oarepo_vocabularies_ui"
    ui_serializer_class = (
        "oarepo_vocabularies.resources.records.ui.VocabularyUIJSONSerializer"
    )
    api_service = "vocabularies"
    application_id = "OarepoVocabularies"

    templates = {
        "detail": "oarepo_vocabularies_ui.VocabulariesDetail",
        "search": "oarepo_vocabularies_ui.VocabulariesSearch",
        "create": "oarepo_vocabularies_ui.VocabulariesForm",
        "edit": "oarepo_vocabularies_ui.VocabulariesForm",
    }

    routes = {
        "create": "/<vocabulary_type>/_new",
        "edit": "/<vocabulary_type>/<pid_value>/edit",
        "search": "/<vocabulary_type>/",
        "detail": "/<vocabulary_type>/<pid_value>",
        "export": "/<vocabulary_type>/<pid_value>/export/<export_format>",
    }
    config_routes = {
        "form_config": "/<vocabulary_type>/form",
    }
    error_handlers = {
        **RecordsUIResourceConfig.error_handlers,
        VocabularyTypeDoesNotExist: "vocabulary_type_does_not_exist",
    }
    components = [
        PermissionsComponent,
        VocabularyRecordsComponent,
        VocabularyFormDepositVocabularyOptionsComponent,
        VocabularySearchComponent,
        CustomFieldsComponent,
    ]

    # request_vocabulary_type_args = {"vocabulary_type": ma.fields.Str()}
    request_vocabulary_type_args = VocabularyTypeValidationSchema

    request_form_config_view_args = {"vocabulary_type": ma.fields.Str()}

    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/{id}"),
        "edit": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/{id}/edit"),
        "search": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/"),
        "create": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/_new"),
    }

    @property
    def ui_links_search(self):
        return {
            **pagination_links("{+ui}{+url_prefix}{vocabulary_type}/{?args*}"),
            "create": Link("{+ui}{+url_prefix}{vocabulary_type}/_new"),
        }

    def vocabulary_props_config(self, vocabulary_type):
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(
            vocabulary_type, {}
        )

    def _get_custom_fields_ui_config(self, key, view_args=None, **kwargs):
        if key == "OAREPO_VOCABULARIES_HIERARCHY_CF":
            return []
        return current_app.config.get("VOCABULARIES_CF_UI", {}).get(
            view_args["vocabulary_type"], []
        )

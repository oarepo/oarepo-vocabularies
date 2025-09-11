#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource for vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import marshmallow as ma
from flask import current_app
from flask_resources import (
    resource_requestctx,
)
from invenio_records_resources.services import Link, pagination_links
from invenio_vocabularies.records.models import VocabularyType
from oarepo_ui.resources.components import (
    AllowedHtmlTagsComponent,
    PermissionsComponent,
)
from oarepo_ui.resources.components.custom_fields import CustomFieldsComponent
from oarepo_ui.resources.records.config import RecordsUIResourceConfig

from oarepo_vocabularies.errors import VocabularyTypeDoesNotExistError
from oarepo_vocabularies.ui.resources.components.deposit import (
    DepositVocabularyOptionsComponent,
)
from oarepo_vocabularies.ui.resources.components.search import VocabularySearchComponent
from oarepo_vocabularies.ui.resources.components.vocabulary_ui_resource import (
    VocabularyRecordsComponent,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from typing import Any, ClassVar

    from flask.typing import ErrorHandlerCallable
    from invenio_records_resources.services.base.config import ServiceConfig
    from invenio_records_resources.services.base.service import Service


class VocabularyFormDepositVocabularyOptionsComponent(DepositVocabularyOptionsComponent):
    """Add specific vocabularies to the deposit form."""

    always_included_vocabularies: ClassVar[list] = ["languages"]

    def form_config(self, *, form_config: dict, **kwargs: Any) -> None:
        """Add languages vocabulary if not present, so that it is always available in the deposit form."""
        super().form_config(form_config=form_config, **kwargs)

        if "languages" not in form_config["vocabularies"]:
            form_config["vocabularies"]["languages"] = []

        if not form_config["vocabularies"]["languages"]:
            form_config["vocabularies"]["languages"] = [{"text": "English", "value": "en"}]


class VocabularyTypeValidationSchema(ma.Schema):
    """Vocabulary type validation schema."""

    vocabulary_type = ma.fields.String()

    def load(self, data: Mapping[str, Any] | Iterable[Mapping[str, Any]], *args: Any, **kwargs: Any) -> dict | None:  # noqa: ARG002
        """Load marshmallow data and validate vocabulary type existence."""
        vocabulary_type = data.get("vocabulary_type")
        # TODO: this will not be needed once specialized vocabs get their own resource
        allowed_specialized_vocabularies = current_app.config.get("OAREPO_VOCABULARIES_SPECIALIZED_SERVICES", [])

        try:
            if (
                VocabularyType.query.filter_by(id=vocabulary_type).one_or_none()
                or vocabulary_type in allowed_specialized_vocabularies.values()
            ):
                return {"vocabulary_type": vocabulary_type}
            raise VocabularyTypeDoesNotExistError(f"Vocabulary type {vocabulary_type} does not exist.")

        except VocabularyTypeDoesNotExistError as e:
            raise VocabularyTypeDoesNotExistError from e
        except Exception as e:
            raise VocabularyTypeDoesNotExistError(f"Vocabulary type {vocabulary_type} does not exist.") from e


class InvenioVocabulariesUIResourceConfig(RecordsUIResourceConfig):
    """Invenio Vocabularies UI Resource Config."""

    template_folder = "../templates"
    url_prefix = "/vocabularies/"
    blueprint_name = "oarepo_vocabularies_ui"
    ui_serializer_class = "oarepo_vocabularies.resources.records.ui.VocabularyUIJSONSerializer"
    api_service = "vocabularies"
    application_id = "OarepoVocabularies"

    templates: ClassVar[dict[str, str]] = {
        "detail": "oarepo_vocabularies_ui.VocabulariesDetail",
        "search": "oarepo_vocabularies_ui.VocabulariesSearch",
        "create": "oarepo_vocabularies_ui.VocabulariesForm",
        "edit": "oarepo_vocabularies_ui.VocabulariesForm",
    }

    routes: ClassVar[dict[str, str]] = {
        "create": "/<type>/_new",
        "edit": "/<type>/<pid_value>/edit",
        "search": "/<type>/",
        "detail": "/<type>/<pid_value>",
        "export": "/<type>/<pid_value>/export/<export_format>",
    }
    config_routes: ClassVar[dict[str, str]] = {
        "form_config": "/<type>/form",
    }
    error_handlers: Mapping[type[Exception], str | ErrorHandlerCallable] = {
        **RecordsUIResourceConfig.error_handlers,
        VocabularyTypeDoesNotExistError: "vocabulary_type_does_not_exist",
    }
    components: ClassVar[list] = [
        PermissionsComponent,
        VocabularyRecordsComponent,
        VocabularyFormDepositVocabularyOptionsComponent,
        VocabularySearchComponent,
        CustomFieldsComponent,
        AllowedHtmlTagsComponent,
    ]

    request_vocabulary_type_args = VocabularyTypeValidationSchema

    request_form_config_view_args: ClassVar[dict[str, ma.fields.Field]] = {"type": ma.fields.Str()}

    # TODO: add ui_links_item with self, edit, search, create

    @property
    def ui_links_search(self) -> dict:
        """UI Search links."""
        return {
            **pagination_links("{+ui}{+url_prefix}{type}/{?args*}"),
            "create": Link("{+ui}{+url_prefix}{type}/_new"),
        }

    def vocabulary_props_config(self, vocabulary_type: str) -> dict:
        """Get vocabulary properties config for a vocabulary type if available."""
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(vocabulary_type, {})

    def _get_custom_fields_ui_config(self, key: str, view_args: dict | None = None) -> list:
        """Get custom fields config for a vocabulary type if available."""
        if key == "OAREPO_VOCABULARIES_HIERARCHY_CF":
            return []
        return current_app.config.get("VOCABULARIES_CF_UI", {}).get(view_args["vocabulary_type"], [])

    def _get_specialized_service_config(self, vocabulary_type: str) -> Service | None:
        """Get specialized service for a vocabulary type if available.

        Returns None if no specialized service exists.
        """
        if (
            vocabulary_type
            and vocabulary_type in current_app.config.get("OAREPO_VOCABULARIES_SPECIALIZED_SERVICES", {}).values()
        ):
            from oarepo_vocabularies.proxies import current_oarepo_vocabularies

            return current_oarepo_vocabularies.get_specialized_service(vocabulary_type)
        return None

    # adapt to search options of each specialized service if available
    def search_available_sort_options(self, api_config: ServiceConfig) -> dict:
        """Get the available sort options for the current vocabulary type."""
        vocabulary_type = resource_requestctx.view_args.get("vocabulary_type")
        specialized_service = self._get_specialized_service_config(vocabulary_type)

        if specialized_service:
            return specialized_service.config.search.sort_options

        return api_config.search.sort_options

    def search_active_sort_options(self, api_config: ServiceConfig) -> list:
        """Get the active sort options for the current vocabulary type."""
        vocabulary_type = resource_requestctx.view_args.get("vocabulary_type")
        specialized_service = self._get_specialized_service_config(vocabulary_type)

        if specialized_service:
            return list(specialized_service.config.search.sort_options.keys())

        return list(api_config.search.sort_options.keys())

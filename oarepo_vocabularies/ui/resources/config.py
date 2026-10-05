# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI Resource for vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override

import marshmallow as ma
from flask import current_app
from invenio_records_resources.services import pagination_endpoint_links
from invenio_records_resources.services.base.links import (
    EndpointLink,
)
from invenio_vocabularies.records.models import VocabularyType
from oarepo_ui.resources.components import (
    AllowedHtmlTagsComponent,
    PermissionsComponent,
)
from oarepo_ui.resources.components.custom_fields import CustomFieldsComponent
from oarepo_ui.resources.components.multilingual_field_languages import (
    MultilingualFieldLanguagesComponent,
)
from oarepo_ui.resources.records.config import RecordsUIResourceConfig

from oarepo_vocabularies.errors import VocabularyTypeDoesNotExistError
from oarepo_vocabularies.resources.config import (
    VocabularySearchRequestArgsSchema,
)
from oarepo_vocabularies.resources.records.ui import VocabularyUIJSONSerializer
from oarepo_vocabularies.ui.resources.components.search import VocabularySearchComponent
from oarepo_vocabularies.ui.resources.components.vocabulary_type_and_props import (
    VocabularyTypeAndProps,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, ClassVar

    from flask.typing import ErrorHandlerCallable
    from invenio_access.permissions import Identity
    from invenio_records_resources.services import Link
    from invenio_records_resources.services.records.config import RecordServiceConfig
    from oarepo_ui.resources.components.base import UIResourceComponent


class VocabularyTypeValidationSchema(ma.Schema):
    """Vocabulary type validation schema."""

    vocabulary_type = ma.fields.String()

    @override
    def load(self, data: Mapping[str, Any], *args: Any, **kwargs: Any) -> dict | None:
        """Load marshmallow data and validate vocabulary type existence."""
        _, _ = args, kwargs
        vocabulary_type = data.get("type")

        try:
            if VocabularyType.query.filter_by(id=vocabulary_type).one_or_none():
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
    model_name = "vocabularies"
    templates: Mapping[str, str | None] = {
        "record_detail": "oarepo_vocabularies_ui.VocabulariesDetail",
        "search": "oarepo_vocabularies_ui.VocabulariesSearch",
        "create": "oarepo_vocabularies_ui.VocabulariesForm",
        "deposit_edit": "oarepo_vocabularies_ui.VocabulariesForm",
    }

    routes: Mapping[str, str] = {
        "create": "/<type>/_new",
        "deposit_edit": "/<type>/<pid_value>/edit",
        "search": "/<type>/",
        "record_detail": "/<type>/<pid_value>",
        "record_export": "/<type>/<pid_value>/export/<export_format>",
    }
    config_routes: Mapping[str, str] = {
        "form_config": "/<type>/form",
    }
    error_handlers: Mapping[type[Exception], str | ErrorHandlerCallable] = {
        **RecordsUIResourceConfig.error_handlers,
        VocabularyTypeDoesNotExistError: "vocabulary_type_does_not_exist",
    }
    # Accepted here only so content negotiation lets the request through; the actual
    # response is a redirect to the matching API endpoint (see vocabulary_content_negotiation),
    # so no real response handler is needed for these mimetypes.
    response_handlers: ClassVar[Mapping[str, Any]] = {
        **RecordsUIResourceConfig.response_handlers,
        "text/turtle": None,
        "application/n-triples": None,
        "application/ld+json": None,
        "application/rdf+xml": None,
        "application/json": None,
    }
    components: ClassVar[list[UIResourceComponent]] = [
        PermissionsComponent,
        VocabularySearchComponent,
        CustomFieldsComponent,
        AllowedHtmlTagsComponent,
        MultilingualFieldLanguagesComponent,
        VocabularyTypeAndProps,
    ]

    @property
    @override
    def ui_serializer(self) -> VocabularyUIJSONSerializer:
        """UI serializer."""
        return VocabularyUIJSONSerializer()

    request_form_config_view_args: ClassVar[dict[str, ma.fields.Field]] = {"type_": ma.fields.Str(data_key="type")}
    request_search_args = VocabularySearchRequestArgsSchema
    request_vocabulary_type_args = VocabularyTypeValidationSchema

    @property
    @override
    def ui_links_item(self) -> Mapping[str, EndpointLink]:
        """UI Item links."""
        return {
            "self": EndpointLink(
                "oarepo_vocabularies_ui.detail",
                vars=lambda record, vars_: vars_.update(
                    {
                        "type": record.data["type"],
                        "pid_value": record.data["id"],
                    }
                ),
                params=["type", "pid_value"],
            ),
            "edit": EndpointLink(
                "oarepo_vocabularies_ui.deposit_edit",
                vars=lambda record, vars_: vars_.update(
                    {
                        "type": record.data["type"],
                        "pid_value": record.data["id"],
                    }
                ),
                params=["type", "pid_value"],
            ),
            "search": EndpointLink(
                "oarepo_vocabularies_ui.search",
                vars=lambda record, vars_: vars_.update({"type": record.data["type"]}),
                params=["type"],
            ),
            "create": EndpointLink(
                "oarepo_vocabularies_ui.create",
                vars=lambda record, vars_: vars_.update({"type": record.data["type"]}),
                params=["type"],
            ),
        }

    @property
    @override
    def ui_links_search(self) -> Mapping[str, Link | EndpointLink]:
        """UI Search links."""
        return {
            **pagination_endpoint_links("oarepo_vocabularies_ui.search", params=["type"]),
            "create": EndpointLink(
                "oarepo_vocabularies_ui.create",
                vars=lambda _obj, vars_: vars_.pop("args", None),
                params=["type"],
            ),
        }

    def vocabulary_props_config(self, vocabulary_type: str) -> Any:
        """Get vocabulary properties config for a vocabulary type if available."""
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(vocabulary_type, {})

    @override
    def _get_custom_fields_ui_config(
        self,
        key: str,
        vocabulary_type: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Get custom fields config for a vocabulary type if available."""
        _, _ = key, kwargs
        vocabularies_cf_ui = current_app.config.get("VOCABULARIES_CF_UI") or {}
        return vocabularies_cf_ui.get(vocabulary_type, [])

    # adapt to search options of each specialized service if available
    @override
    def search_available_sort_options(
        self,
        api_config: RecordServiceConfig,
        identity: Identity,
    ) -> dict[str, dict[str, Any]]:
        """Get the available sort options for the current vocabulary type."""
        _ = identity
        return cast("dict", api_config.search.sort_options)

    @override
    def search_active_sort_options(self, api_config: RecordServiceConfig, identity: Identity) -> list[str]:
        """Get the active sort options for the current vocabulary type."""
        _ = identity
        return list(api_config.search.sort_options.keys())

    @override
    def search_endpoint_url(self, identity: Identity, overrides: dict[str, str] | None = None, **kwargs: Any) -> str:
        """Get the search endpoint URL for the current vocabulary type."""
        _ = identity, kwargs
        return EndpointLink("vocabularies.search", params=["type"]).expand(
            {},
            {
                "type": overrides["vocabularyType"] if overrides else None,
            },
        )

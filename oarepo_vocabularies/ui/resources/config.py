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

from typing import TYPE_CHECKING, ClassVar, cast

import marshmallow as ma
from flask import current_app
from flask_resources import (
    MultiDictSchema,
)
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
from oarepo_ui.resources.records.config import RecordsUIResourceConfig

from oarepo_vocabularies.errors import VocabularyTypeDoesNotExistError
from oarepo_vocabularies.resources.config import VocabularySearchRequestArgsSchema, VocabularyTypeRequestArgsSchema
from oarepo_vocabularies.resources.records.ui import VocabularyUIJSONSerializer
from oarepo_vocabularies.ui.resources.components.search import VocabularySearchComponent

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

    def load(self, data: Mapping[str, Any], *args: Any, **kwargs: Any) -> dict | None:  # noqa: ARG002
        """Load marshmallow data and validate vocabulary type existence."""
        vocabulary_type = data.get("type")

        try:
            if VocabularyType.query.filter_by(id=vocabulary_type).one_or_none():  # type: ignore[attr-defined]
                return {"type": vocabulary_type}
            raise VocabularyTypeDoesNotExistError(f"Vocabulary type {vocabulary_type} does not exist.")

        except VocabularyTypeDoesNotExistError as e:
            raise VocabularyTypeDoesNotExistError from e
        except Exception as e:
            raise VocabularyTypeDoesNotExistError(f"Vocabulary type {vocabulary_type} does not exist.") from e


# TODO: will be removed in favour of administration view
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
        "detail": "oarepo_vocabularies_ui.VocabulariesDetail",
        "search": "oarepo_vocabularies_ui.VocabulariesSearch",
        "create": "oarepo_vocabularies_ui.VocabulariesForm",
        "edit": "oarepo_vocabularies_ui.VocabulariesForm",
    }

    routes: Mapping[str, str] = {
        "deposit_create": "/<type>/_new",
        "deposit_edit": "/<type>/<pid_value>/edit",
        "search": "/<type>/",
        "record_detail": "/<type>/<pid_value>",
        "export": "/<type>/<pid_value>/export/<export_format>",
    }
    config_routes: Mapping[str, str] = {
        "form_config": "/<type>/form",
    }
    error_handlers: Mapping[type[Exception], str | ErrorHandlerCallable] = {
        **RecordsUIResourceConfig.error_handlers,
        VocabularyTypeDoesNotExistError: "vocabulary_type_does_not_exist",
    }
    components: ClassVar[list[UIResourceComponent]] = [  # type: ignore[override]
        PermissionsComponent,
        VocabularySearchComponent,
        CustomFieldsComponent,
        AllowedHtmlTagsComponent,
    ]
    request_view_args = MultiDictSchema.from_dict(
        {"pid_value": ma.fields.Str(), "type_": ma.fields.Str(data_key="type")}
    )

    @property
    def ui_serializer(self) -> VocabularyUIJSONSerializer:
        """UI serializer."""
        return VocabularyUIJSONSerializer()

    request_form_config_view_args: ClassVar[dict[str, ma.fields.Field]] = {"type_": ma.fields.Str(data_key="type")}  # type: ignore[override]
    request_search_args = VocabularySearchRequestArgsSchema
    request_vocabulary_type_args = VocabularyTypeRequestArgsSchema

    @property
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
                "oarepo_vocabularies_ui.edit",
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
    def ui_links_search(self) -> Mapping[str, Link | EndpointLink]:
        """UI Search links."""
        return {
            **pagination_endpoint_links("oarepo_vocabularies_ui.search", params=["type"]),
            "create": EndpointLink(
                "oarepo_vocabularies_ui.create",
                vars=lambda obj, vars_: vars_.pop("args", None),  # noqa: ARG005
                params=["type"],
            ),
        }

    def vocabulary_props_config(self, vocabulary_type: str) -> Any:
        """Get vocabulary properties config for a vocabulary type if available."""
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(vocabulary_type, {})

    def _get_custom_fields_ui_config(self, key: str, **kwargs: Any) -> Any:  # noqa: ARG002
        """Get custom fields config for a vocabulary type if available."""
        vocabularies_cf_ui = current_app.config.get("VOCABULARIES_CF_UI") or {}
        return vocabularies_cf_ui.get(key, [])

    # adapt to search options of each specialized service if available
    def search_available_sort_options(
        self,
        api_config: RecordServiceConfig,
        identity: Identity,  # noqa: ARG002
    ) -> dict[str, dict[str, Any]]:
        """Get the available sort options for the current vocabulary type."""
        return cast("dict", api_config.search.sort_options)

    def search_active_sort_options(self, api_config: RecordServiceConfig, identity: Identity) -> list[str]:  # noqa: ARG002 added for inheritance
        """Get the active sort options for the current vocabulary type."""
        return list(api_config.search.sort_options.keys())

    def search_endpoint_url(self, identity: Identity, overrides: dict[str, str] | None = None, **kwargs: Any) -> str:  # noqa: ARG002
        """Get the search endpoint URL for the current vocabulary type."""
        return cast(
            "str",
            EndpointLink("oarepo_vocabularies_ui.search", params=["type"]).expand(
                {},
                {
                    "type": overrides["type"] if overrides else None,
                },
            ),
        )

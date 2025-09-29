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

from functools import partial
from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem


class VocabularyRecordsComponent(UIResourceComponent):
    """Component is used for UI search & display of a vocabulary item."""

    def before_ui_search(
        self,
        *,
        extra_context: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        search_options: dict,
        ui_links: dict,  # noqa: ARG002
        **kwargs: Any,
    ) -> None:
        """Process the data before the search page is rendered."""
        vocabulary_type = kwargs.get("type_")

        if not vocabulary_type:
            raise ValueError("Vocabulary type is required.")

        api_service = self.resource.api_service  # type: ignore[attr-defined]
        search_options.setdefault(
            "endpoint",
            api_service.config.links_search["self"].expand(None, {"type": vocabulary_type}),
        )
        search_options.setdefault("overrides", {})
        search_options["overrides"]["type"] = vocabulary_type

    def before_ui_detail(
        self,
        *,
        api_record: RecordItem,
        record: dict,  # noqa: ARG002
        identity: Identity,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,
        **kwargs: Any,
    ) -> None:
        """Prepare the context for displaying a vocabulary item detail page."""
        vocabulary_type = kwargs.get("type_")
        if not vocabulary_type:
            raise ValueError("Vocabulary type is required")

        api_service = self.resource.api_service  # type: ignore[attr-defined]
        search_options = {
            "api_config": api_service.config,
            "identity": identity,
            "endpoint": api_service.config.links_search["self"].expand(None, {"type": vocabulary_type}),
            "initial_filters": [["h-parent", api_record["id"]]],
        }
        search_config = partial(self.config.search_app_config, **search_options)  # type: ignore[attr-defined]
        extra_context.setdefault("search_app_config", search_config)
        extra_context["type"] = vocabulary_type
        extra_context["props"] = self.config.vocabulary_props_config(vocabulary_type)  # type: ignore[attr-defined]

    def before_ui_edit(  # noqa: PLR0913
        self,
        *,
        api_record: RecordItem,
        record: dict,  # noqa: ARG002
        data: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        form_config: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        **kwargs: Any,
    ) -> None:
        """Prepare the form configuration for editing a vocabulary item."""
        vocabulary_type = kwargs.get("type_")
        if not vocabulary_type:
            raise ValueError("Vocabulary type is required")

        form_config.setdefault("vocabularyProps", self.config.vocabulary_props_config(vocabulary_type))  # type: ignore[attr-defined]
        form_config.setdefault(
            "updateUrl",
            api_record["links"].get("self", None),
        )
        form_config["type"] = vocabulary_type

    def before_ui_create(
        self,
        *,
        data: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        form_config: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        **kwargs: Any,
    ) -> None:
        """Prepare the form configuration for creating a new vocabulary item."""
        vocabulary_type = kwargs.get("type_")

        if not vocabulary_type:
            raise ValueError("Vocabulary type is required")

        api_service = self.resource.api_service  # type: ignore[attr-defined]
        form_config.setdefault("props", self.config.vocabulary_props_config(vocabulary_type))  # type: ignore[attr-defined]
        form_config["createUrl"] = f"/api{api_service.config.url_prefix}{vocabulary_type}"
        form_config["type"] = vocabulary_type

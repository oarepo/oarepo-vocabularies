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
        view_args: dict,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Process the data before the search page is rendered."""
        vocabulary_type = view_args["vocabulary_type"]
        api_service = self.resource.api_service
        search_options.setdefault(
            "endpoint",
            api_service.config.links_search["self"].expand(None, {"type": vocabulary_type, "api": "/api"}),
        )
        search_options.setdefault("overrides", {})
        search_options["overrides"]["vocabularyType"] = vocabulary_type

    def before_ui_detail(
        self,
        *,
        extra_context: dict,
        identity: Identity,
        view_args: dict,
        api_record: RecordItem,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Prepare the context for displaying a vocabulary item detail page."""
        vocabulary_type = view_args["vocabulary_type"]
        api_service = self.resource.api_service
        search_options = {
            "api_config": api_service.config,
            "identity": identity,
            "endpoint": api_service.config.links_search["self"].expand(None, {"type": vocabulary_type, "api": "/api"}),
            "initial_filters": [["h-parent", api_record["id"]]],
        }
        search_config = partial(self.config.search_app_config, **search_options)
        extra_context.setdefault("search_app_config", search_config)
        extra_context["vocabularyType"] = vocabulary_type
        extra_context["vocabularyProps"] = self.config.vocabulary_props_config(vocabulary_type)

    def before_ui_edit(self, *, form_config: dict, api_record: RecordItem, view_args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Prepare the form configuration for editing a vocabulary item."""
        vocabulary_type = view_args["vocabulary_type"]
        form_config.setdefault("vocabularyProps", self.config.vocabulary_props_config(vocabulary_type))
        form_config.setdefault(
            "updateUrl",
            api_record["links"].get("self", None),
        )
        form_config["vocabularyType"] = vocabulary_type

    def before_ui_create(self, *, form_config: dict, view_args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Prepare the form configuration for creating a new vocabulary item."""
        vocabulary_type = view_args["vocabulary_type"]
        api_service = self.resource.api_service
        form_config.setdefault("vocabularyProps", self.config.vocabulary_props_config(vocabulary_type))
        form_config["createUrl"] = f"/api{api_service.config.url_prefix}{vocabulary_type}"
        form_config["vocabularyType"] = vocabulary_type

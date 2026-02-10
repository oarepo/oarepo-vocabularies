#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource component for vocabulary search."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem


class VocabularyTypeAndProps(UIResourceComponent):
    """Process the data before the search page is rendered."""

    def before_ui_search(
        self,
        *,
        identity: Identity,  # noqa: ARG002
        search_options: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        vocabulary_type: str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Process the data before the search page is rendered."""
        search_options["headers"] = {"Accept": "application/json"}
        if vocabulary_type:
            search_options["overrides"]["vocabularyType"] = vocabulary_type
            search_options["overrides"]["vocabularyProps"] = (
                self.config.vocabulary_props_config(vocabulary_type)
            )  # type: ignore[attr-defined]

    def form_config(  # noqa: PLR0913  too many arguments
        self,
        *,
        api_record: RecordItem,  # noqa: ARG002
        record: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        form_config: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        vocabulary_type: str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Add vocabulary type and props to the form config as in."""
        if vocabulary_type:
            form_config["vocabularyType"] = vocabulary_type
            form_config["vocabularyProps"] = self.config.vocabulary_props_config(
                vocabulary_type
            )  # type: ignore[attr-defined]

    def before_ui_detail(  # noqa: PLR0913  too many arguments
        self,
        *,
        api_record: RecordItem,  # noqa: ARG002
        record: dict,  # noqa: ARG002
        identity: Identity,  # noqa: ARG002
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,
        vocabulary_type: str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Process the data before the detail page is rendered."""
        extra_context["vocabularyType"] = vocabulary_type
        if vocabulary_type:
            extra_context["vocabularyProps"] = self.config.vocabulary_props_config(
                vocabulary_type
            )  # type: ignore[attr-defined]

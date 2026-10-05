# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI Resource component for vocabulary search."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity


class VocabularySearchComponent(UIResourceComponent):
    """Process the data before the search page is rendered."""

    def before_ui_search(
        self,
        *,
        identity: Identity,  # noqa: ARG002
        search_options: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Process the data before the search page is rendered."""
        search_options["headers"] = {"Accept": "application/json"}

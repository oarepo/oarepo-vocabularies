# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI Resource component for vocabulary search."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity


class VocabularySearchComponent(UIResourceComponent):
    """Process the data before the search page is rendered."""

    @override
    def before_ui_search(
        self,
        *,
        identity: Identity,
        search_options: dict,
        ui_links: dict,
        extra_context: dict,
        **kwargs: Any,
    ) -> None:
        """Process the data before the search page is rendered."""
        search_options["headers"] = {"Accept": "application/json"}

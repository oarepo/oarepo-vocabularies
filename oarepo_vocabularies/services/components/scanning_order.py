# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Component to handle scanning order in vocabulary searches."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.records.components import ServiceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from opensearch_dsl import Search


class ScanningOrderComponent(ServiceComponent):
    """Component to handle scanning order in vocabulary searches."""

    def scan(self, identity: Identity, search: Search, params: dict[str, Any]) -> Search:
        """Modify the search to include scanning order if specified in params."""
        if params.get("preserve_order"):
            return search.params(preserve_order=True)
        return search

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Component to handle scanning order in vocabulary searches."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.records.components import ServiceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from opensearch_dsl import Search


class ScanningOrderComponent(ServiceComponent):
    """Component to handle scanning order in vocabulary searches."""

    def scan(self, identity: Identity, search: Search, params: dict[str, Any]) -> Search:  # noqa: ARG002
        """Modify the search to include scanning order if specified in params."""
        if params.get("preserve_order"):
            return search.params(preserve_order=True)
        return search

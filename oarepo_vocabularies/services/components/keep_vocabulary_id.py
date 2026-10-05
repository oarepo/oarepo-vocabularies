# SPDX-FileCopyrightText: 2024-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Component to keep the vocabulary ID unchanged on updates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_records_resources.services.records.components import ServiceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record


class KeepVocabularyIdComponent(ServiceComponent):
    """Component to keep the vocabulary ID unchanged on updates."""

    @override
    def update(self, identity: Identity, **kwargs: Any) -> None:
        """Keep the vocabulary ID unchanged on updates."""
        data: dict[str, Any] = kwargs.get("data", {})
        record: Record | None = kwargs.get("record")

        if "id" not in data and record:
            data["id"] = record["id"]

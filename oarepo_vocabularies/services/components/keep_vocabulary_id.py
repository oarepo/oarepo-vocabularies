#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Component to keep the vocabulary ID unchanged on updates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.records.components import ServiceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record


class KeepVocabularyIdComponent(ServiceComponent):
    """Component to keep the vocabulary ID unchanged on updates."""

    def update(self, identity: Identity, **kwargs: Any) -> None:  # noqa: ARG002
        """Keep the vocabulary ID unchanged on updates."""
        data: dict[str, Any] = kwargs.get("data", {})
        record: Record | None = kwargs.get("record")

        if "id" not in data and record:
            data["id"] = record["id"]

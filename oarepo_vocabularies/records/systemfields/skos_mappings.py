# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Identifiers system field for vocabulary records."""

from __future__ import annotations

from typing import Any

from invenio_records.systemfields import SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin


class SKOSMappingSystemField(MappingSystemFieldMixin, SystemField):
    """System field handling the mapping of identifiers."""

    @property
    def mapping(self) -> dict[str, Any]:
        """Get the mapping for the identifiers field."""
        key = self.key
        if key is None:
            raise ValueError("Field key cannot be None")

        return {
            key: {
                "type": "nested",
                "properties": {
                    "identifier": {"type": "keyword"},
                    "scheme": {"type": "keyword"},
                    "relation": {
                        "type": "keyword",
                    },
                },
            }
        }

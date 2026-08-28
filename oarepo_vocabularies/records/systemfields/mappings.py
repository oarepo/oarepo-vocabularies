#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Identifiers system field for vocabulary records."""

from __future__ import annotations

from typing import Any

from invenio_records.systemfields import SystemField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin


class MappingsSystemField(MappingSystemFieldMixin, SystemField):
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

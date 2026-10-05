# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Custom fields system field for vocabulary records."""

from __future__ import annotations

from typing import Any, override

from invenio_records.systemfields import DictField
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin


class VocabularyCustomFieldsSystemField(MappingSystemFieldMixin, DictField):
    """Dict system field for custom fields, mapped as a dynamic object."""

    @property
    @override
    def mapping(self) -> dict[str, Any]:
        """Get the mapping for the custom fields field."""
        key = self.key
        if key is None:
            raise ValueError("Field key cannot be None")

        return {
            key: {
                "type": "object",
                "dynamic": True,
            }
        }

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""System fields for relations in vocabularies."""

from __future__ import annotations

from typing import Any

from invenio_records.systemfields.relations.results import RelationResult
from invenio_records_resources.records.systemfields.relations import PIDRelation
from invenio_vocabularies.records.api import Vocabulary


class ParentVocabularyItemRelationResult(RelationResult):
    """Result of a parent vocabulary item relation."""

    def _lookup_id(self, *args: Any, **kwargs: Any) -> tuple[str, str]:  # noqa: ARG002
        """Lookup the vocabulary type and ID of the related record."""
        id_ = super()._lookup_id()
        vocabulary_type = self.record["type"]["id"]

        return (vocabulary_type, id_)


class ParentVocabularyItemRelation(PIDRelation):
    """Relation to a parent vocabulary item."""

    result_cls = ParentVocabularyItemRelationResult


class ParentVocabularyPIDField:
    """Parent vocabulary PID field."""

    def resolve(self, id_: tuple[str, str]) -> Vocabulary:
        """Resolve the PID to a specific type Vocabulary record."""
        vocabulary_type, item_id = id_
        return Vocabulary.pid.with_type_ctx(vocabulary_type).resolve(item_id)  # type: ignore[attr-defined]

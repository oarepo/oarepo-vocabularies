#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from invenio_search.engine import dsl
from oarepo_runtime.services.generators import ConditionalGenerator

if TYPE_CHECKING:
    from collections.abc import Sequence

    from invenio_records_permissions.generators import Generator as InvenioGenerator


class IfVocabularyType(ConditionalGenerator):
    """Generator allowing operations on specific vocabulary type only (e.g. languages)."""

    def __init__(self, type_: str, then_: Sequence[InvenioGenerator], else_: Sequence[InvenioGenerator]):
        """Init the condition with specific vocabulary type."""
        super().__init__(then_, else_)
        self.type = type_

    def _condition(self, **kwargs: Any) -> bool:
        """Check if the vocabulary type matches, if passed directly or in record."""
        if "type" in kwargs:
            return cast("bool", kwargs["type"] == self.type)

        if "data" in kwargs:
            record = kwargs["data"]
            if record and "type" in record:
                return cast("bool", record["type"] == self.type)

        if "record" in kwargs:
            record = kwargs["record"]
            if record and "type" in record:
                return cast("bool", record["type"]["id"] == self.type)

        return False

    def _query_instate(self, **context: Any) -> dsl.query.Query:  # noqa: ARG002
        # Vocabulary type is already filtered in invenio_vocabularies/services/services.py by passing extra filter."""
        return dsl.Q("match_all")

    def query_filter(self, **context: Any) -> dsl.query.Query:
        """Apply then."""
        # Vocabulary type is already filtered in invenio_vocabularies/services/services.py by passing extra filter."""
        return cast("dsl.query.Query", super()._make_query(self.then_, **context))


class IfNonDangerousVocabularyOperation(ConditionalGenerator):
    """Generator allowing non-dangerous operations."""

    def __init__(self, then_: Any, else_: Any = ()):
        """Init the condition."""
        if then_ and not isinstance(then_, (list, tuple)):
            then_ = [then_]
        if else_ and not isinstance(else_, (list, tuple)):
            else_ = [else_]
        super().__init__(then_, else_)

    def _condition(self, **kwargs: Any) -> Any:
        """Condition to choose generators set."""
        if "data" not in kwargs:
            raise ValueError(
                "Data are not provided. "
                "Make sure you use the generator on update operation "
                "and use the oarepo fork of invenio-records-resources"
            )
        data = kwargs["data"]
        record = kwargs["record"]

        # changing parent is a dangerous operation as indexed records that use the vocab item needs to be reindexed
        if data.get("hierarchy", {}).get("parent") != record.hierarchy.to_dict().get("parent"):
            return False

        # changing id is a very dangerous operation as records that use the vocab item will be broken
        return data.get("id") == record.get("id")

    def _query_instate(self, **context: Any) -> dsl.query.Query:  # noqa: ARG002
        # Vocabulary type is already filtered in invenio_vocabularies/services/services.py by passing extra filter."""
        return dsl.Q("match_all")

#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AnyUser,
    ConditionalGenerator,
    Disable,
    SystemProcess,
)

if TYPE_CHECKING:
    from invenio_records_permissions.generators import Generator


class VocabulariesPermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    can_search: ClassVar[list[Generator]] = [SystemProcess(), AnyUser()]
    can_read: ClassVar[list[Generator]] = [SystemProcess(), AnyUser()]
    can_list_vocabularies: ClassVar[list[Generator]] = [SystemProcess(), AnyUser()]

    can_create: ClassVar[list[Generator]] = [SystemProcess()]
    can_update: ClassVar[list[Generator]] = [SystemProcess()]
    can_delete: ClassVar[list[Generator]] = [SystemProcess()]
    can_manage: ClassVar[list[Generator]] = [SystemProcess()]

    def __getattr__(self, item: str) -> Any:
        """Dynamically return can_<action> lists."""
        for mth in (
            "can_search",
            "can_read",
            "can_create",
            "can_update",
            "can_delete",
            "can_manage",
        ):
            if item.startswith(mth + "_"):
                return getattr(self, mth)
        raise AttributeError(item)

    @property
    def generators(self) -> Any:
        """List of Needs generators for self.action.

        Defaults to Disable() if no can_<self.action> defined.
        """
        return getattr(self, "can_" + self.action, [Disable()])


class NonDangerousVocabularyOperation(ConditionalGenerator):
    """Generator allowing non-dangerous operations."""

    def __init__(self, then_: Any, else_: Any = ()):
        """Init the condition."""
        if then_ and not isinstance(then_, (list, tuple)):
            then_ = [then_]
        if else_ and not isinstance(else_, (list, tuple)):
            else_ = [else_]
        super().__init__(then_, else_)

    def _condition(self, **kwargs: Any) -> bool:
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
        if data.get("hierarchy", {}).get("parent") != record.get("hierarchy", {}).get("parent"):
            return False

        # changing id is a very dangerous operation as records that use the vocab item will be broken
        return data.get("id") == record.get("id")

# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, Disable, SystemProcess, ConditionalGenerator


class VocabulariesPermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    can_search = [SystemProcess(), AnyUser()]
    can_read = [SystemProcess(), AnyUser()]
    can_list_vocabularies = [SystemProcess(), AnyUser()]

    can_create = [SystemProcess()]
    can_update = [SystemProcess()]
    can_delete = [SystemProcess()]
    can_manage = [SystemProcess()]

    def __getattr__(self, item):
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
    def generators(self):
        """List of Needs generators for self.action.

        Defaults to Disable() if no can_<self.action> defined.
        """
        return getattr(self, "can_" + self.action, [Disable()])


class NonDangerousVocabularyOperation(ConditionalGenerator):
    def __init__(self, then_, else_=()):
        if then_ and not isinstance(then_, (list, tuple)):
            then_ = [then_]
        if else_ and not isinstance(else_, (list, tuple)):
            else_ = [else_]
        super().__init__(then_, else_)

    def _condition(self, **kwargs):
        """Condition to choose generators set."""
        if "data" not in kwargs:
            raise ValueError("Data are not provided. "
                             "Make sure you use the generator on update operation "
                             "and use the oarepo fork of invenio-records-resources")
        data = kwargs["data"]
        record = kwargs["record"]

        # changing parent is a dangerous operation as indexed records that use the vocab item needs to be reindexed
        if data.get("hierarchy", {}).get("parent") != record.get("hierarchy", {}).get("parent"):
            return False

        # changing id is a very dangerous operation as records that use the vocab item will be broken
        if data.get("id") != record.get("id"):
            return False

        return True

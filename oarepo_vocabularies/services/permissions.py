# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, Disable, SystemProcess


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

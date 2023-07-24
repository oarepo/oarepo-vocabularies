# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_permissions.policies.base import BasePermissionPolicy


class PermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    can_search = [SystemProcess(), AnyUser()]
    can_read = [SystemProcess(), AnyUser()]

    can_create = [SystemProcess(), AnyUser()]
    can_update = [SystemProcess(), AnyUser()]
    can_delete = [SystemProcess(), AnyUser()]
    can_manage = [SystemProcess(), AnyUser()]


class VocabulariesPermissionPolicy(BasePermissionPolicy):
    # NOTE: probably change to an authenticated user later.
    can_list_vocabularies = [SystemProcess(), AnyUser()]

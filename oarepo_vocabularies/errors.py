#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Errors for vocabularies."""

from __future__ import annotations

from invenio_i18n import lazy_gettext as _


class VocabularyTypeDoesNotExistError(Exception):
    """The record is already in the community."""

    description = _("Vocabulary type does not exist.")

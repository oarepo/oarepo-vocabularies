# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Errors for vocabularies."""

from __future__ import annotations

from invenio_i18n import lazy_gettext as _


class VocabularyTypeDoesNotExistError(Exception):
    """The record is already in the community."""

    description = _("Vocabulary type does not exist.")

# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI proxies for oarepo-vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .ext import InvenioVocabulariesAppExtension

    current_vocabularies_ui: InvenioVocabulariesAppExtension

current_vocabularies_ui = LocalProxy(lambda: current_app.extensions["oarepo_vocabularies_ui"])
"""Proxy to the instantiated ui extension."""

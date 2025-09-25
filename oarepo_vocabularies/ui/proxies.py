#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI proxies for oarepo-vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .ext import InvenioVocabulariesAppExtension

    current_vocabularies_ui: InvenioVocabulariesAppExtension

current_vocabularies_ui = LocalProxy(lambda: current_app.extensions["oarepo_vocabularies_ui"])  # type: ignore[assignment]
"""Proxy to the instantiated ui extension."""

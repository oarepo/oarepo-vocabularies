# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Oarepo vocabularies proxies."""

from __future__ import annotations

import typing
from typing import cast

from flask import current_app
from werkzeug.local import LocalProxy

if typing.TYPE_CHECKING:
    from .ext import OARepoVocabularies
    from .services.service import VocabularyTypeService


def _ext_proxy(attr: str) -> LocalProxy:
    return LocalProxy(lambda: getattr(current_app.extensions["oarepo-vocabularies"], attr))


current_oarepo_vocabularies = cast(
    "OARepoVocabularies", LocalProxy(lambda: current_app.extensions["oarepo-vocabularies"])
)

current_type_service = cast("VocabularyTypeService", _ext_proxy("type_service"))
"""Proxy to the instantiated vocabulary type service."""

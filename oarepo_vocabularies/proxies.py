#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Oarepo vocabularies proxies."""

from __future__ import annotations

import typing

from flask import current_app
from werkzeug.local import LocalProxy

if typing.TYPE_CHECKING:
    from .ext import OARepoVocabularies
    from .services.service import VocabularyTypeService

    current_oarepo_vocabularies: OARepoVocabularies
    current_type_service: VocabularyTypeService


def _ext_proxy(attr: str) -> LocalProxy:
    return LocalProxy(lambda: getattr(current_app.extensions["oarepo-vocabularies"], attr))


current_oarepo_vocabularies = LocalProxy(lambda: current_app.extensions["oarepo-vocabularies"])  # type: ignore[assignment]

current_type_service = _ext_proxy("type_service")  # type: ignore[assignment]
"""Proxy to the instantiated vocabulary type service."""

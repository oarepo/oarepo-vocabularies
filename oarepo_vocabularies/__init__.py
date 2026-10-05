# SPDX-FileCopyrightText: 2022-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo vocabularies package provides vocabulary fields extension for Invenio-Vocabularies."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("oarepo-vocabularies")
except PackageNotFoundError:
    __version__ = "0.0.0dev0+unknown"

__all__ = ("__version__",)

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""CLI commands for vocabularies."""

from __future__ import annotations

from oarepo_runtime.cli import oarepo


@oarepo.group(name="vocabularies", help="Vocabularies tools.")
def vocabularies() -> None:
    """Runtime grpoup for vocabularies."""

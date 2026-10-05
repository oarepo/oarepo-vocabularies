# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""CLI commands for vocabularies."""

from __future__ import annotations

from oarepo_runtime.cli import oarepo


@oarepo.group(name="vocabularies", help="Vocabularies tools.")
def vocabularies() -> None:
    """Runtime grpoup for vocabularies."""

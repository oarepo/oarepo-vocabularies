# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""OARepo vocabularies branch."""

from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "1765979850"
down_revision = None
branch_labels = ("oarepo_vocabularies",)
depends_on = ("4f365fced43f",)  # depends on vocabularies module


def upgrade() -> None:
    """Upgrade database."""


def downgrade() -> None:
    """Downgrade database."""

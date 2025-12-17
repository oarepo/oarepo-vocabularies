# noqa: N999
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Create UI blueprints."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Blueprint, Flask

from oarepo_vocabularies.ui.proxies import current_vocabularies_ui


def create_blueprint(app: Flask) -> Blueprint:
    """Blueprint for the routes and resources provided by current ui's resource."""
    with app.app_context():
        return current_vocabularies_ui.resource.as_blueprint()


def create_vocabulary_type_blueprint(app: Flask) -> Blueprint:
    """Blueprint for the routes and resources provided by current ui's type resource."""
    with app.app_context():
        return current_vocabularies_ui.type_resource.as_blueprint()

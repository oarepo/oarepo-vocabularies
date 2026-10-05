# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Init blueprints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask
    from flask.sansio.blueprints import BlueprintSetupState


def create_app_blueprint(app: Flask) -> Blueprint:  # noqa: ARG001
    """Create app blueprint."""
    blueprint = Blueprint("oarepo_vocabularies", __name__, template_folder="templates")
    blueprint.record_once(init_create_app_blueprint)
    return blueprint


def init_create_app_blueprint(state: BlueprintSetupState) -> None:
    """Init app blueprint."""
    app = state.app
    ext = app.extensions["oarepo-vocabularies"]

    # Register service.
    sregistry = app.extensions["invenio-records-resources"].registry
    if ext.type_service.config.service_id not in sregistry._services:  # noqa: SLF001
        sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

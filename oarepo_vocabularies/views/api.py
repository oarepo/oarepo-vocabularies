# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Init API blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Blueprint, Flask
    from flask.sansio.blueprints import BlueprintSetupState


def create_api_blueprint(app: Flask) -> Blueprint:
    """Create MymodelRecord blueprint."""
    blueprint = app.extensions["oarepo-vocabularies"].type_resource.as_blueprint()
    blueprint.record_once(init_create_api_blueprint)
    return blueprint


def init_create_api_blueprint(state: BlueprintSetupState) -> None:
    """Init app."""
    app = state.app
    ext = app.extensions["oarepo-vocabularies"]

    # Register service.
    sregistry = app.extensions["invenio-records-resources"].registry

    if ext.type_service.config.service_id not in sregistry._services:  # noqa: SLF001 there is no public call to get all services
        sregistry.register(ext.type_service, service_id=ext.type_service.config.service_id)

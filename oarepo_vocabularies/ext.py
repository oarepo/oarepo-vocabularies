#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo extension of Invenio-Vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.records.links import (
    RecordEndpointLink,
)
from invenio_vocabularies.services.permissions import PermissionPolicy

from oarepo_vocabularies.cli import vocabularies as vocabularies_cli  # noqa

if TYPE_CHECKING:
    from flask import Flask


class OARepoVocabularies:
    """OARepo extension of Invenio-Vocabularies."""

    def __init__(self, app: Flask | None = None) -> None:
        """Extension initialization."""
        self.type_resource = None
        self.type_service = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.init_services(app)
        self.init_resource(app)
        app.extensions["oarepo-vocabularies"] = self

    def init_services(self, app: Flask) -> None:
        """Initialize services."""
        self.type_service = app.config["OAREPO_VOCABULARY_TYPE_SERVICE"](
            config=app.config["OAREPO_VOCABULARY_TYPE_SERVICE_CONFIG"](),
        )

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        from . import config

        for k in dir(config):
            if k.startswith("OAREPO_VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
            if k.startswith("OAREPO_VOCABULARY_"):
                app.config.setdefault(k, getattr(config, k))
            if k.startswith("VOCABULARIES"):
                app.config.setdefault(k, getattr(config, k))
        app.config.setdefault("VOCABULARIES_FACET_CACHE_SIZE", config.VOCABULARIES_FACET_CACHE_SIZE)
        app.config.setdefault("VOCABULARIES_FACET_CACHE_TTL", config.VOCABULARIES_FACET_CACHE_TTL)
        app.config.setdefault("INVENIO_VOCABULARY_TYPE_METADATA", config.INVENIO_VOCABULARY_TYPE_METADATA)

        if "OAREPO_PERMISSIONS_PRESETS" not in app.config:
            app.config["OAREPO_PERMISSIONS_PRESETS"] = {}

        for k in config.OAREPO_VOCABULARIES_PERMISSIONS_PRESETS:
            if k not in app.config["OAREPO_PERMISSIONS_PRESETS"]:
                app.config["OAREPO_PERMISSIONS_PRESETS"][k] = config.OAREPO_VOCABULARIES_PERMISSIONS_PRESETS[k]

    def init_resource(self, app: Flask) -> None:
        """Initialize resources."""
        self.type_resource = app.config["OAREPO_VOCABULARY_TYPE_RESOURCE"](
            config=app.config["OAREPO_VOCABULARY_TYPE_RESOURCE_CONFIG"](),
            service=self.type_service,
        )

    def get_config(self, vocabulary_name_or_dict: dict | str) -> Any:
        """Get specific vocabulary configuration."""
        if isinstance(vocabulary_name_or_dict, dict):
            vocabulary_name = vocabulary_name_or_dict.get("id")
        else:
            vocabulary_name = vocabulary_name_or_dict

        vocabulary_type_metadata = self.app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {})
        return vocabulary_type_metadata.get(vocabulary_name, {})


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    awards_service = app.extensions["invenio-vocabularies"].awards_service
    awards_service.config.url_prefix = "/awards/"
    awards_service.config.links_item["self_html"] = RecordEndpointLink(
        "oarepo_vocabularies_ui.record_detail",
        vars=lambda record, vars_: vars_.update(
            {
                "type": "awards",
                "pid_value": record.pid.pid_value,
            }
        ),
        params=["type", "pid_value"],
    )
    awards_service.config.permission_policy_cls = PermissionPolicy

    affiliations_service = app.extensions["invenio-vocabularies"].affiliations_service
    affiliations_service.config.links_item["self_html"] = RecordEndpointLink(
        "oarepo_vocabularies_ui.record_detail",
        vars=lambda record, vars_: vars_.update(
            {
                "type": "affiliations",
                "pid_value": record.pid.pid_value,
            }
        ),
        params=["type", "pid_value"],
    )
    affiliations_service.config.permission_policy_cls = PermissionPolicy

    funders_service = app.extensions["invenio-vocabularies"].funders_service
    funders_service.config.links_item["self_html"] = RecordEndpointLink(
        "oarepo_vocabularies_ui.record_detail",
        vars=lambda record, vars_: vars_.update(
            {
                "type": "funders",
                "pid_value": record.pid.pid_value,
            }
        ),
        params=["type", "pid_value"],
    )
    funders_service.config.permission_policy_cls = PermissionPolicy

    names_service = app.extensions["invenio-vocabularies"].names_service
    names_service.config.search.sort_options["name"] = {
        "title": ("Name"),
        "fields": ["name_sort"],
    }
    names_service.config.links_item["self_html"] = RecordEndpointLink(
        "oarepo_vocabularies_ui.record_detail",
        vars=lambda record, vars_: vars_.update(
            {
                "type": "names",
                "pid_value": record.pid.pid_value,
            }
        ),
        params=["type", "pid_value"],
    )
    names_service.config.permission_policy_cls = PermissionPolicy

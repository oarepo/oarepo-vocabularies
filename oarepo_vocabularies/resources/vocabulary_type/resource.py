#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Resource for vocabulary types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g
from flask_resources import Resource, response_handler, route

if TYPE_CHECKING:
    from invenio_records_resources.resources import RecordResourceConfig
    from invenio_records_resources.services.base import Service


class VocabularyTypeResource(Resource):
    """Resource for vocabulary types."""

    def __init__(self, config: RecordResourceConfig, service: Service) -> None:
        """Init the vocabulary type resource."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self) -> list:
        """Create the URL rules for the resource."""
        routes = self.config.routes

        return [route("GET", routes["list"], self.list)]

    @response_handler(many=True)
    def list(self) -> tuple[dict, int]:
        """Perform a search over the items."""
        identity = g.identity
        hits = self.service.search(identity=identity)  # type: ignore[attr-defined]
        return hits.to_dict(), 200

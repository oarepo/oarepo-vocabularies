# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Resource for vocabulary types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from flask import g
from flask_resources import Resource, response_handler, route

if TYPE_CHECKING:
    import builtins

    from invenio_records_resources.resources import RecordResourceConfig

    from oarepo_vocabularies.services.service import VocabularyTypeService


class VocabularyTypeResource(Resource):
    """Resource for vocabulary types."""

    def __init__(self, config: RecordResourceConfig, service: VocabularyTypeService) -> None:
        """Init the vocabulary type resource."""
        super().__init__(config)
        self.service = service

    @override
    def create_url_rules(self) -> builtins.list[dict[str, Any]]:
        """Create the URL rules for the resource."""
        routes = self.config.routes

        return [route("GET", routes["list"], self.list)]

    @response_handler(many=True)
    def list(self) -> tuple[dict, int]:
        """Perform a search over the items."""
        identity = g.identity
        hits = self.service.search(identity=identity)
        return hits.to_dict(), 200

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask import g
from flask_resources import Resource, response_handler, route


class VocabularyTypeResource(Resource):
    def __init__(self, config, service):
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        routes = self.config.routes

        return [route("GET", routes["list"], self.list)]

    @response_handler(many=True)
    def list(self):
        """Perform a search over the items."""
        identity = g.identity
        hits = self.service.search(identity=identity)
        return hits.to_dict(), 200

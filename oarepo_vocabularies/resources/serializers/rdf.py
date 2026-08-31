#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Base RDF graph serializer for vocabulary records."""

from __future__ import annotations

from typing import Any, ClassVar, cast

from flask_resources.serializers.base import BaseSerializer
from rdflib import Graph

from oarepo_vocabularies.resources.serializers.graph import as_graph


class RDFSerializer(BaseSerializer):
    """Base serializer converting vocabulary records to an RDF graph representation.

    Subclasses set ``rdflib_format`` to the rdflib serialization plugin name to use
    (e.g. "turtle", "nt").
    """

    rdflib_format: ClassVar[str]

    def serialize_object(self, obj: dict[str, Any]) -> str:
        """Serialize a single vocabulary record."""
        return cast("str", as_graph(obj).serialize(format=self.rdflib_format))

    def serialize_object_list(self, obj_list: dict[str, Any]) -> str:
        """Serialize a search result of vocabulary records as a single merged document."""
        graph = Graph()
        for hit in obj_list["hits"]["hits"]:
            graph += as_graph(hit)
        return cast("str", graph.serialize(format=self.rdflib_format))

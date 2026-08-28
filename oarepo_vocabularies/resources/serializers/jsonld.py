#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""JSON-LD (framed SKOS/RDF) serializer for vocabulary records."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from flask_resources.serializers.base import BaseSerializer
from pyld import jsonld
from rdflib import Graph

from oarepo_vocabularies.resources.serializers.graph import _oarepo_namespace, as_graph

if TYPE_CHECKING:
    from pyld.options import FrameOptions

_JSONLD_CONTEXT: dict[str, Any] = {
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dct": "http://purl.org/dc/terms/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "id": "@id",
    "type": "@type",
    "prefLabel": "skos:prefLabel",
    "notation": "skos:notation",
    "inScheme": {"@id": "skos:inScheme", "@type": "@id"},
    "broader": {"@id": "skos:broader", "@type": "@id"},
    "exactMatch": {"@id": "skos:exactMatch", "@type": "@id"},
    "broadMatch": {"@id": "skos:broadMatch", "@type": "@id"},
    "narrowMatch": {"@id": "skos:narrowMatch", "@type": "@id"},
    "closeMatch": {"@id": "skos:closeMatch", "@type": "@id"},
    "relatedMatch": {"@id": "skos:relatedMatch", "@type": "@id"},
    "description": "dct:description",
    "keyword": "dcat:keyword",
}

# @once: embed a referenced node (e.g. the shared ConceptScheme) fully only the first time
# it's encountered; later references are left as plain @id strings to avoid duplication.
# @omitDefault: drop frame-listed properties entirely (e.g. "broader") when a concept has
# no value for them, rather than emitting them as null.
# pyld's FrameOptions.embed Literal omits "@once", even though pyld's own implementation
# uses it as the actual default (see pyld.jsonld.frame's `options.setdefault('embed', '@once')`).
_FRAME_OPTIONS: FrameOptions = {"embed": "@once", "omitDefault": True}  # type: ignore[assignment]


def _jsonld_context() -> dict[str, Any]:
    """Build the JSON-LD @context, adding the proprietary oarepo namespace as @vocab."""
    return {**_JSONLD_CONTEXT, "@vocab": str(_oarepo_namespace())}


def _jsonld_frame(context: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON-LD frame selecting SKOS concepts and embedding known relations inline."""
    return {
        "@context": context,
        "@type": "skos:Concept",
        "@embed": "@once",
        "@omitDefault": True,
        "skos:inScheme": {},
        "skos:broader": {},
    }


def _as_jsonld(graph: Graph) -> dict[str, Any]:
    """Frame a graph into a compact, embedded JSON-LD document."""
    context = _jsonld_context()
    doc = json.loads(graph.serialize(format="json-ld"))
    return cast("dict[str, Any]", jsonld.frame(doc, _jsonld_frame(context), _FRAME_OPTIONS))


class JsonLdSerializer(BaseSerializer):
    """Serializer converting vocabulary records to a framed, SKOS-compliant JSON-LD document."""

    def serialize_object(self, obj: dict[str, Any]) -> str:
        """Serialize a single vocabulary record."""
        return json.dumps(_as_jsonld(as_graph(obj)))

    def serialize_object_list(self, obj_list: dict[str, Any]) -> str:
        """Serialize a search result of vocabulary records as a single framed JSON-LD document."""
        graph = Graph()
        for hit in obj_list["hits"]["hits"]:
            graph += as_graph(hit)
        return json.dumps(_as_jsonld(graph))

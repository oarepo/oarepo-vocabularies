#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""SKOS/RDF graph serialization of vocabulary records."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from flask import current_app
from invenio_base.urls import invenio_url_for
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS

_SKOS_MAPPING_PREDICATES = {
    "exactMatch": SKOS.exactMatch,
    "broadMatch": SKOS.broadMatch,
    "narrowMatch": SKOS.narrowMatch,
    "closeMatch": SKOS.closeMatch,
    "relatedMatch": SKOS.relatedMatch,
}


def _oarepo_namespace() -> Namespace:
    """Proprietary oarepo-vocabularies namespace for round-tripping non-SKOS metadata.

    Covers fields that have no standard RDF/SKOS equivalent (UI ``icon``, legacy ``props``) but
    are needed to reconstruct the record, including its presentation logic, in another
    oarepo-vocabularies instance. Not intended for external semantic interop.

    Configurable via ``OAREPO_VOCABULARY_NAMESPACE_URI``; falls back to a URI derived from the
    running instance's own vocabulary listing endpoint when not set.
    """
    namespace_uri = current_app.config.get("OAREPO_VOCABULARY_NAMESPACE_URI") or (
        f"{invenio_url_for('vocabulary_type_app.list')}#oarepo-"
    )
    return Namespace(namespace_uri)


def as_graph(data: dict[str, Any]) -> Graph:
    """Convert a serialized vocabulary record to a graphlib's graph representation.

    :param data:
        A vocabulary record as dumped by the service's schema (e.g. ``RecordItem.to_dict()``).

    :return:
        A graphlib's graph representation of the record which is SKOS compliant and includes
        the "mappings" field for extra mapping. Also includes "icon" and "props", encoded under
        a proprietary oarepo-vocabularies namespace, so the record (including its presentation
        logic) can be reconstructed by another oarepo-vocabularies instance. These are not
        deduplicated against the SKOS-standard triples derived from "mappings" -- some overlap
        is expected and ignored on import. The record's hierarchy parent/ancestors (if any) are
        also included as skos:broader triples pointing to the ancestor concepts.
    """
    vocabulary_type = data["type"]
    pid_value = data["id"]

    graph = Graph()
    subject = URIRef(
        invenio_url_for(
            "oarepo_vocabularies_ui.record_detail",
            type=vocabulary_type,
            pid_value=pid_value,
        )
    )
    scheme = URIRef(invenio_url_for("oarepo_vocabularies_ui.search", type=vocabulary_type))

    graph.add((subject, RDF.type, SKOS.Concept))
    graph.add((subject, SKOS.notation, Literal(pid_value)))
    graph.add((subject, SKOS.inScheme, scheme))

    graph.add((scheme, RDF.type, SKOS.ConceptScheme))
    scheme_name = (
        current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(vocabulary_type, {}).get("title", {})
    )
    for lang, label in scheme_name.items():
        graph.add((scheme, SKOS.prefLabel, Literal(label, lang=lang)))

    for lang, label in (data.get("title") or {}).items():
        graph.add((subject, SKOS.prefLabel, Literal(label, lang=lang)))

    for lang, description in (data.get("description") or {}).items():
        graph.add((subject, DCTERMS.description, Literal(description, lang=lang)))

    for tag in data.get("tags") or []:
        graph.add((subject, DCAT.keyword, Literal(tag)))

    oarepo_ns = _oarepo_namespace()

    icon = data.get("icon")
    if icon:
        graph.add((subject, oarepo_ns.icon, Literal(icon)))

    for key, value in (data.get("props") or {}).items():
        graph.add((subject, oarepo_ns[f"props-{quote(key, safe='')}"], Literal(value)))

    for mapping in data.get("mappings") or []:
        identifier = mapping.get("identifier")
        predicate = _SKOS_MAPPING_PREDICATES.get(mapping.get("relation"))
        if identifier and predicate is not None:
            graph.add((subject, predicate, URIRef(identifier)))

    for ancestor_id in (data.get("hierarchy") or {}).get("ancestors") or []:
        ancestor = URIRef(
            invenio_url_for(
                "oarepo_vocabularies_ui.record_detail",
                type=vocabulary_type,
                pid_value=ancestor_id,
            )
        )
        graph.add((subject, SKOS.broader, ancestor))

    return graph

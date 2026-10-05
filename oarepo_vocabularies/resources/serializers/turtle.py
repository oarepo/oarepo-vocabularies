# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Turtle (SKOS/RDF) serializer for vocabulary records."""

from __future__ import annotations

from oarepo_vocabularies.resources.serializers.rdf import RDFSerializer


class TurtleSerializer(RDFSerializer):
    """Serializer converting vocabulary records to a SKOS-compliant Turtle document."""

    rdflib_format = "turtle"

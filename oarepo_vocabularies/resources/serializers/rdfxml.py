# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""RDF/XML (SKOS/RDF) serializer for vocabulary records."""

from __future__ import annotations

from oarepo_vocabularies.resources.serializers.rdf import RDFSerializer


class RdfXmlSerializer(RDFSerializer):
    """Serializer converting vocabulary records to a SKOS-compliant RDF/XML document."""

    rdflib_format = "pretty-xml"

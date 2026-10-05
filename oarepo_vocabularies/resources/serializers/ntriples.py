# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""N-Triples (SKOS/RDF) serializer for vocabulary records."""

from __future__ import annotations

from oarepo_vocabularies.resources.serializers.rdf import RDFSerializer


class NTriplesSerializer(RDFSerializer):
    """Serializer converting vocabulary records to a SKOS-compliant N-Triples document."""

    rdflib_format = "nt"

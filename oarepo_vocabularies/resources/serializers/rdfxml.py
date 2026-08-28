#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""RDF/XML (SKOS/RDF) serializer for vocabulary records."""

from __future__ import annotations

from oarepo_vocabularies.resources.serializers.rdf import RDFSerializer


class RdfXmlSerializer(RDFSerializer):
    """Serializer converting vocabulary records to a SKOS-compliant RDF/XML document."""

    rdflib_format = "pretty-xml"

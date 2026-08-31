#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for the RDF content-negotiated response handlers on the vocabularies resource.

Covers text/turtle, application/n-triples, application/rdf+xml and application/ld+json --
they all serialize the same underlying graph (see resources/serializers/graph.py), so the
response bodies are parsed back with rdflib and checked against the same triples. JSON-LD
framing has additional shape guarantees (no @graph for a single record, embedded relations,
omitted-not-null missing properties) that are format-specific and covered separately in
test_jsonld.py.
"""

from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_vocabularies.records.api import Vocabulary
from rdflib import Graph
from rdflib.namespace import SKOS

RDF_FORMATS = [
    pytest.param("text/turtle", "turtle", id="turtle"),
    pytest.param("application/n-triples", "nt", id="ntriples"),
    pytest.param("application/rdf+xml", "xml", id="rdfxml"),
    pytest.param("application/ld+json", "json-ld", id="jsonld"),
]


@pytest.mark.parametrize(("mimetype", "rdflib_format"), RDF_FORMATS)
def test_read(client, eng_with_mapping, mimetype, rdflib_format):
    response = client.get("/api/vocabularies/languages/eng", headers={"Accept": mimetype})

    assert response.status_code == 200
    assert response.mimetype == mimetype

    graph = Graph()
    graph.parse(data=response.get_data(as_text=True), format=rdflib_format)

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, SKOS.exactMatch, None) in graph


@pytest.mark.parametrize(("mimetype", "rdflib_format"), RDF_FORMATS)
def test_read_via_ui_content_negotiation(client, eng_with_mapping, mimetype, rdflib_format):
    redirect_response = client.get(
        "/vocabularies/languages/eng",
        headers={"Accept": mimetype},
        follow_redirects=False,
    )
    assert redirect_response.status_code == 302
    assert "/api/vocabularies/languages/eng" in redirect_response.location

    # follow the redirect explicitly, re-sending the Accept header, since the test client's
    # follow_redirects does not resend custom request headers on the redirected request
    response = client.get(redirect_response.location, headers={"Accept": mimetype})

    assert response.status_code == 200
    assert response.mimetype == mimetype

    graph = Graph()
    graph.parse(data=response.get_data(as_text=True), format=rdflib_format)

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, SKOS.exactMatch, None) in graph


@pytest.mark.parametrize(("mimetype", "rdflib_format"), RDF_FORMATS)
def test_search(
    app, db, cache, lang_type, vocab_cf, client, search_clear, clear_vocabulary_permissions, mimetype, rdflib_format
):
    vocab_service.create(
        system_identity,
        {"id": "eng", "title": {"en": "English"}, "type": "languages"},
    )
    vocab_service.create(
        system_identity,
        {"id": "cze", "title": {"en": "Czech"}, "type": "languages"},
    )
    Vocabulary.index.refresh()

    response = client.get("/api/vocabularies/languages", headers={"Accept": mimetype})

    assert response.status_code == 200
    assert response.mimetype == mimetype

    graph = Graph()
    graph.parse(data=response.get_data(as_text=True), format=rdflib_format)

    subjects = {str(s) for s in graph.subjects(SKOS.notation, None)}
    assert any(s.endswith("/vocabularies/languages/eng") for s in subjects)
    assert any(s.endswith("/vocabularies/languages/cze") for s in subjects)

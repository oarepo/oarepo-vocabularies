#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for the text/turtle response handler on the vocabularies resource."""

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_vocabularies.records.api import Vocabulary
from rdflib import Graph
from rdflib.namespace import SKOS


def test_turtle_read(app, db, cache, lang_type, vocab_cf, client, search_clear, clear_vocabulary_permissions):
    vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "cs": "Anglictina"},
            "type": "languages",
            "mappings": [
                {
                    "identifier": "https://schema.org/Book",
                    "scheme": "https://schema.org/",
                    "relation": "exactMatch",
                },
            ],
        },
    )

    response = client.get("/api/vocabularies/languages/eng", headers={"Accept": "text/turtle"})

    assert response.status_code == 200
    assert response.mimetype == "text/turtle"

    graph = Graph()
    graph.parse(data=response.get_data(as_text=True), format="turtle")

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, SKOS.exactMatch, None) in graph


def test_turtle_search(app, db, cache, lang_type, vocab_cf, client, search_clear, clear_vocabulary_permissions):
    vocab_service.create(
        system_identity,
        {"id": "eng", "title": {"en": "English"}, "type": "languages"},
    )
    vocab_service.create(
        system_identity,
        {"id": "cze", "title": {"en": "Czech"}, "type": "languages"},
    )
    Vocabulary.index.refresh()

    response = client.get("/api/vocabularies/languages", headers={"Accept": "text/turtle"})

    assert response.status_code == 200
    assert response.mimetype == "text/turtle"

    graph = Graph()
    graph.parse(data=response.get_data(as_text=True), format="turtle")

    subjects = {str(s) for s in graph.subjects(SKOS.notation, None)}
    assert any(s.endswith("/vocabularies/languages/eng") for s in subjects)
    assert any(s.endswith("/vocabularies/languages/cze") for s in subjects)

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for the JSON-LD-specific framing behavior of the application/ld+json response handler.

Basic read/redirect/search coverage lives in test_rdf_serializations.py, shared with the other
RDF formats. This file only covers shape guarantees unique to framing: no @graph wrapper for a
single record, inline-embedded relations, and omitted (not null) missing properties.
"""

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from invenio_vocabularies.records.api import Vocabulary


def test_jsonld_flat_single_record(client, eng_with_mapping):
    response = client.get("/api/vocabularies/languages/eng", headers={"Accept": "application/ld+json"})

    assert response.status_code == 200

    doc = response.json
    # flat, framed object -- no @graph wrapper for a single record
    assert "@graph" not in doc
    assert doc["@context"]
    assert doc["id"].endswith("/vocabularies/languages/eng")
    assert doc["type"] == "skos:Concept"
    assert doc["exactMatch"] == "https://schema.org/Book"

    # inScheme is embedded inline, not a bare reference
    assert isinstance(doc["inScheme"], dict)
    assert doc["inScheme"]["id"].endswith("/vocabularies/languages/")
    assert doc["inScheme"]["type"] == "skos:ConceptScheme"

    # concepts without a broader relation don't get "broader": null
    assert "broader" not in doc


def test_jsonld_search_embeds_scheme_once_and_omits_missing_broader(
    app, db, cache, lang_type, vocab_cf, client, search_clear, clear_vocabulary_permissions
):
    vocab_service.create(
        system_identity,
        {"id": "eng", "title": {"en": "English"}, "type": "languages"},
    )
    vocab_service.create(
        system_identity,
        {
            "id": "eng.US",
            "title": {"en": "English (US)"},
            "type": "languages",
            "hierarchy": {"parent": "eng"},
        },
    )
    Vocabulary.index.refresh()

    response = client.get("/api/vocabularies/languages", headers={"Accept": "application/ld+json"})

    assert response.status_code == 200

    doc = response.json
    # multiple records genuinely need @graph
    nodes = doc["@graph"]
    assert len(nodes) == 2

    eng = next(n for n in nodes if n["id"].endswith("/vocabularies/languages/eng"))
    eng_us = next(n for n in nodes if n["id"].endswith("/vocabularies/languages/eng.US"))

    # root concept has no broader -- omitted rather than null
    assert "broader" not in eng
    # child concept's broader is embedded inline (its own id/type/prefLabel), not a bare reference
    assert isinstance(eng_us["broader"], dict)
    assert eng_us["broader"]["id"].endswith("/vocabularies/languages/eng")
    assert eng_us["broader"]["type"] == "skos:Concept"

    # the shared ConceptScheme is embedded fully once (first occurrence) and left as a bare
    # reference afterwards (@embed: @once), rather than being duplicated in every node
    embedded_schemes = [n for n in nodes if isinstance(n.get("inScheme"), dict)]
    referenced_schemes = [n for n in nodes if isinstance(n.get("inScheme"), str)]
    assert len(embedded_schemes) == 1
    assert len(referenced_schemes) == 1

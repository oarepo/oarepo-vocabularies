#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for the SKOS/RDF graph serialization of vocabulary records."""

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service
from rdflib import Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF, SKOS

from oarepo_vocabularies.resources.serializers.graph import _oarepo_namespace, as_graph


def test_as_graph(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "cs": "Anglictina"},
            "description": {"en": "The English language", "cs": "Anglicky jazyk"},
            "tags": ["germanic", "west-germanic"],
            "icon": "flag",
            "props": {"alpha3CodeNative": "eng", "custom.key with space": "value"},
            "type": "languages",
            "mappings": [
                {
                    "identifier": "https://schema.org/Book",
                    "scheme": "https://schema.org/",
                    "relation": "exactMatch",
                },
                {
                    "identifier": "https://example.org/eng-related",
                    "scheme": "https://example.org/",
                    "relation": "relatedMatch",
                },
            ],
        },
    )
    graph = as_graph(result.to_dict())

    subjects = set(graph.subjects())
    subject = next(s for s in subjects if str(s).endswith("/vocabularies/languages/eng"))

    assert (subject, RDF.type, SKOS.Concept) in graph
    assert (subject, SKOS.notation, None) in graph
    assert (subject, SKOS.prefLabel, None) in graph

    pref_labels = {(o.value, o.language) for o in graph.objects(subject, SKOS.prefLabel) if isinstance(o, Literal)}
    assert pref_labels == {("English", "en"), ("Anglictina", "cs")}

    descriptions = {
        (o.value, o.language) for o in graph.objects(subject, DCTERMS.description) if isinstance(o, Literal)
    }
    assert descriptions == {("The English language", "en"), ("Anglicky jazyk", "cs")}

    tags = {str(o) for o in graph.objects(subject, DCAT.keyword)}
    assert tags == {"germanic", "west-germanic"}

    mapping_predicates = {p for p in graph.predicates(subject) if str(p).startswith(str(SKOS))}
    assert SKOS.exactMatch in mapping_predicates
    assert SKOS.relatedMatch in mapping_predicates

    assert (subject, SKOS.exactMatch, None) in graph
    exact_matches = set(graph.objects(subject, SKOS.exactMatch))
    assert str(next(iter(exact_matches))) == "https://schema.org/Book"

    related_matches = set(graph.objects(subject, SKOS.relatedMatch))
    assert str(next(iter(related_matches))) == "https://example.org/eng-related"

    scheme = next(iter(graph.objects(subject, SKOS.inScheme)))
    assert str(scheme).endswith("/vocabularies/languages/")
    assert (scheme, RDF.type, SKOS.ConceptScheme) in graph
    scheme_labels = {(o.value, o.language) for o in graph.objects(scheme, SKOS.prefLabel) if isinstance(o, Literal)}
    assert scheme_labels == {("languages", "en"), ("jazyky", "cs")}

    oarepo_ns = _oarepo_namespace()
    assert (subject, oarepo_ns.icon, Literal("flag")) in graph
    assert (subject, oarepo_ns["props-alpha3CodeNative"], Literal("eng")) in graph
    assert (subject, oarepo_ns["props-custom.key%20with%20space"], Literal("value")) in graph


def test_as_graph_configured_namespace(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions, monkeypatch
):
    monkeypatch.setitem(app.config, "OAREPO_VOCABULARY_NAMESPACE_URI", "https://example.org/ns/vocabularies#")

    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "icon": "flag",
            "type": "languages",
        },
    )
    graph = as_graph(result.to_dict())

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, URIRef("https://example.org/ns/vocabularies#icon"), Literal("flag")) in graph


def test_as_graph_no_mappings(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
    result = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English"},
            "type": "languages",
        },
    )
    graph = as_graph(result.to_dict())

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, RDF.type, SKOS.Concept) in graph
    assert (subject, DCTERMS.description, None) not in graph
    assert (subject, DCAT.keyword, None) not in graph
    mapping_predicates = {
        p
        for p in graph.predicates(subject)
        if p in (SKOS.exactMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.closeMatch, SKOS.relatedMatch)
    }
    assert mapping_predicates == set()


def test_as_graph_hierarchy_broader(app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions):
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
    grand_child = vocab_service.create(
        system_identity,
        {
            "id": "eng.US.TX",
            "title": {"en": "English (US, Texas)"},
            "type": "languages",
            "hierarchy": {"parent": "eng.US"},
        },
    )

    graph = as_graph(grand_child.to_dict())

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng.US.TX"))
    broader = {str(o) for o in graph.objects(subject, SKOS.broader)}
    assert broader == {
        "https://127.0.0.1:5000/vocabularies/languages/eng.US",
        "https://127.0.0.1:5000/vocabularies/languages/eng",
    }


def test_as_graph_no_hierarchy_no_broader(
    app, db, cache, lang_type, vocab_cf, search_clear, clear_vocabulary_permissions
):
    result = vocab_service.create(
        system_identity,
        {"id": "eng", "title": {"en": "English"}, "type": "languages"},
    )
    graph = as_graph(result.to_dict())

    subject = next(s for s in graph.subjects() if str(s).endswith("/vocabularies/languages/eng"))
    assert (subject, SKOS.broader, None) not in graph

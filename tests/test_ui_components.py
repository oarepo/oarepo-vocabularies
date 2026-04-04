#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Tests for vocabulary UI components."""

from __future__ import annotations

import pytest

from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.templating.data import FieldData


@pytest.fixture
def simple_vocabulary_field_data():
    """Create FieldData for a simple vocabulary item."""
    api_data = {
        "id": "langs-en",
        "title": {"en": "English"},
        "type": "languages",
    }
    ui_data = {
        "id": "langs-en",
        "title": {"en": "English"},
        "type": "languages",
    }
    ui_definitions = {
        "children": {
            "id": {"label": "ID"},
            "title": {"label": "Title"},
            "type": {"label": "Type"},
        }
    }
    return FieldData.create(
        api_data=api_data,
        ui_data=ui_data,
        ui_definitions=ui_definitions,
        item_getter=lambda *args, **kwargs: None,
    )


@pytest.fixture
def simple_vocabulary_array_field_data():
    """Create FieldData for an array of simple vocabulary items."""
    api_data = [
        {
            "id": "langs-en",
            "title": {"en": "English"},
            "type": "languages",
        },
        {
            "id": "langs-de",
            "title": {"de": "Deutsch"},
            "type": "languages",
        },
    ]
    ui_data = [
        {
            "id": "langs-en",
            "title": {"en": "English"},
            "type": "languages",
        },
        {
            "id": "langs-de",
            "title": {"de": "Deutsch"},
            "type": "languages",
        },
    ]
    ui_definitions = {
        "children": {
            "id": {"label": "ID"},
            "title": {"label": "Title"},
            "type": {"label": "Type"},
        }
    }
    return FieldData.create(
        api_data=api_data,
        ui_data=ui_data,
        ui_definitions=ui_definitions,
        item_getter=lambda *args, **kwargs: None,
    )


@pytest.fixture
def taxonomy_field_data():
    """Create FieldData for a hierarchical vocabulary (taxonomy) item."""
    api_data = {
        "id": "taxonomy-leaf",
        "title": {"en": "Leaf"},
        "type": "taxonomy_types",
        "hierarchy": {
            "title": [
                {"en": "Root"},
                {"en": "Branch"},
                {"en": "Leaf"},
            ],
            "ancestors": ["taxonomy-root", "taxonomy-branch"],
        },
    }
    ui_data = {
        "id": "taxonomy-leaf",
        "title": {"en": "Leaf"},
        "type": "taxonomy_types",
        "hierarchy": {
            "title": [
                {"en": "Root"},
                {"en": "Branch"},
                {"en": "Leaf"},
            ],
            "ancestors": ["taxonomy-root", "taxonomy-branch"],
        },
    }
    ui_definitions = {
        "children": {
            "id": {"label": "ID"},
            "title": {"label": "Title"},
            "type": {"label": "Type"},
            "hierarchy": {
                "children": {
                    "title": {"label": "Title"},
                    "ancestors": {"label": "Ancestors"},
                }
            },
        }
    }
    return FieldData.create(
        api_data=api_data,
        ui_data=ui_data,
        ui_definitions=ui_definitions,
        item_getter=lambda *args, **kwargs: None,
    )


@pytest.fixture
def taxonomy_array_field_data():
    """Create FieldData for an array of taxonomy items."""
    api_data = [
        {
            "id": "taxonomy-leaf1",
            "title": {"en": "Leaf 1"},
            "type": "taxonomy_types",
            "hierarchy": {
                "title": [
                    {"en": "Root"},
                    {"en": "Leaf 1"},
                ],
                "ancestors": ["taxonomy-root"],
            },
        },
        {
            "id": "taxonomy-leaf2",
            "title": {"en": "Leaf 2"},
            "type": "taxonomy_types",
            "hierarchy": {
                "title": [
                    {"en": "Root"},
                    {"en": "Leaf 2"},
                ],
                "ancestors": ["taxonomy-root"],
            },
        },
    ]
    ui_data = [
        {
            "id": "taxonomy-leaf1",
            "title": {"en": "Leaf 1"},
            "type": "taxonomy_types",
            "hierarchy": {
                "title": [
                    {"en": "Root"},
                    {"en": "Leaf 1"},
                ],
                "ancestors": ["taxonomy-root"],
            },
        },
        {
            "id": "taxonomy-leaf2",
            "title": {"en": "Leaf 2"},
            "type": "taxonomy_types",
            "hierarchy": {
                "title": [
                    {"en": "Root"},
                    {"en": "Leaf 2"},
                ],
                "ancestors": ["taxonomy-root"],
            },
        },
    ]
    ui_definitions = {
        "children": {
            "id": {"label": "ID"},
            "title": {"label": "Title"},
            "type": {"label": "Type"},
            "hierarchy": {
                "children": {
                    "title": {"label": "Title"},
                    "ancestors": {"label": "Ancestors"},
                }
            },
        }
    }
    return FieldData.create(
        api_data=api_data,
        ui_data=ui_data,
        ui_definitions=ui_definitions,
        item_getter=lambda *args, **kwargs: None,
    )


def test_vocabulary_item_simple(app, simple_vocabulary_field_data):
    """Test rendering a simple vocabulary item."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "VocabularyItem",
            d=simple_vocabulary_field_data,
            search_link="/search",
            searchFacet="languages",
        )
        assert "English" in output
        assert "/vocabularies/languages/langs-en" in output
        assert "/search?q=&f=languages:langs-en" in output


def test_vocabulary_item_no_search_link(app, simple_vocabulary_field_data):
    """Test rendering vocabulary item without search link."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "VocabularyItem",
            d=simple_vocabulary_field_data,
            hide_definition=True,
        )
        assert "English" in output
        assert "<span>English</span>" in output
        assert "/vocabularies/" not in output


def test_vocabulary_item_hidden_definition(app, simple_vocabulary_field_data):
    """Test rendering vocabulary item with definition hidden."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "VocabularyItem",
            d=simple_vocabulary_field_data,
            search_link="/search",
            searchFacet="languages",
            hide_definition=True,
        )
        assert "English" in output
        assert "/search?q=&f=languages:langs-en" in output
        assert "DefinitionLink" not in output


def test_vocabulary_array(app, simple_vocabulary_array_field_data):
    """Test rendering an array of vocabulary items."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "VocabularyItem",
            d=simple_vocabulary_array_field_data,
            search_link="/search",
            searchFacet="languages",
        )
        assert "English" in output
        assert "Deutsch" in output
        assert "/vocabularies/languages/langs-en" in output
        assert "/vocabularies/languages/langs-de" in output


def test_taxonomy_item(app, taxonomy_field_data):
    """Test rendering a taxonomy item with breadcrumbs."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "TaxonomyItem",
            d=taxonomy_field_data,
            search_link="/search",
            searchFacet="taxonomy_types",
            vocabulary_type="taxonomy_types",
        )
        assert "Root" in output
        assert "Branch" in output
        assert "Leaf" in output
        assert "ui breadcrumb" in output
        assert "divider" in output
        assert "/vocabularies/taxonomy_types/taxonomy-root" in output
        assert "/vocabularies/taxonomy_types/taxonomy-branch" in output
        assert "/vocabularies/taxonomy_types/taxonomy-leaf" in output


def test_taxonomy_item_no_search(app, taxonomy_field_data):
    """Test rendering taxonomy item without search link."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "TaxonomyItem",
            d=taxonomy_field_data,
            search_link="/search",
            searchFacet="taxonomy_types",
            vocabulary_type="taxonomy_types",
        )
        # Since search_link is provided, it should be rendered
        assert "Leaf" in output
        assert "ui breadcrumb" in output


def test_taxonomy_array(app, taxonomy_array_field_data):
    """Test rendering an array of taxonomy items."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "TaxonomyItem",
            d=taxonomy_array_field_data,
            search_link="/search",
            searchFacet="taxonomy_types",
            vocabulary_type="taxonomy_types",
        )
        assert "Leaf 1" in output
        assert "Leaf 2" in output
        # Should have two breadcrumb divs
        assert output.count("ui breadcrumb") == 2


def test_taxonomy_hidden_definition(app, taxonomy_field_data):
    """Test rendering taxonomy item with definition hidden."""
    with app.app_context():
        output = current_oarepo_ui.catalog.render(
            "TaxonomyItem",
            d=taxonomy_field_data,
            search_link="/search",
            searchFacet="taxonomy_types",
            vocabulary_type="taxonomy_types",
            hide_definition=True,
        )
        assert "Leaf" in output
        assert "ui breadcrumb" in output
        assert "/vocabularies/" not in output  # Definition links should be hidden

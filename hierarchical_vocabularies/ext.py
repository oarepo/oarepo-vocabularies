# -*- coding: utf-8 -*-

"""Invenio module for managing vocabularies."""

from . import config
from .resources.resource import HierarchicalVocabulariesResource
from .services.service import HierarchicalVocabulariesService


class HierarchicalVocabularies(object):
    """Hierarchical-Vocabularies extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        self.service = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_resource(app)
        app.extensions["hierarchical_vocabularies"] = self

    def init_resource(self, app):
        """Initialize Hierarchical-vocabulary resources."""
        # Generic Vocabularies
        self.service = HierarchicalVocabulariesService(
            config=app.config["HVOCABULARIES_SERVICE_CONFIG"],
        )
        self.resource = HierarchicalVocabulariesResource(
            service=self.service,
            config=app.config["HVOCABULARIES_RESOURCE_CONFIG"],
        )

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("HVOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))

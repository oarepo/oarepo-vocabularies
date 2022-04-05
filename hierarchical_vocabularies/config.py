# -*- coding: utf-8 -*-

"""Hierarchical Vocabularies configuration."""


from .resources.resource import HierarchicalVocabulariesResourceConfig
from .services.service import HierarchicalVocabulariesServiceConfig

VOCABULARIES_RESOURCE_CONFIG = HierarchicalVocabulariesResourceConfig
"""Configure the resource."""

VOCABULARIES_SERVICE_CONFIG = HierarchicalVocabulariesServiceConfig
"""Configure the service."""

# -*- coding: utf-8 -*-


"""Hierarchical vocabularies views."""


def create_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["hierarchical_vocabularies"].resource.as_blueprint()

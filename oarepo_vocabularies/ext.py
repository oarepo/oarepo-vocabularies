class OARepoVocabularies(object):
    """OARepo extension of Invenio-Vocabularies."""

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
        app.extensions["oarepo-vocabularies"] = self

    def init_config(self, app):
        """Initialize configuration."""
        from . import config

        for k in dir(config):
            if k.startswith("OAREPO_VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
            if k.startswith("DEFAULT_DATASTREAMS_"):
                app.config.setdefault(k, {}).update(getattr(config, k))
            if k.startswith("DATASTREAMS_CONFIG_GENERATOR_"):
                app.config.setdefault(k, getattr(config, k))
        app.config.setdefault('VOCABULARIES_FACET_CACHE_SIZE', config.VOCABULARIES_FACET_CACHE_SIZE)
        app.config.setdefault('VOCABULARIES_FACET_CACHE_TTL', config.VOCABULARIES_FACET_CACHE_TTL)

    def init_resource(self, app):
        pass

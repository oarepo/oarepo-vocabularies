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
        from . import config, ext_config

        for k in dir(config):
            if k.startswith("OAREPO_VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
            if k.startswith("DEFAULT_DATASTREAMS_"):
                app.config.setdefault(k, {}).update(getattr(config, k))
            if k.startswith("DATASTREAMS_CONFIG_GENERATOR_"):
                app.config.setdefault(k, getattr(config, k))
            if k.startswith("VOCABULARY"):
                app.config.setdefault(k, getattr(config, k))
        app.config.setdefault(
            "VOCABULARIES_FACET_CACHE_SIZE", config.VOCABULARIES_FACET_CACHE_SIZE
        )
        app.config.setdefault(
            "VOCABULARIES_FACET_CACHE_TTL", config.VOCABULARIES_FACET_CACHE_TTL
        )

        if "OAREPO_PERMISSIONS_PRESETS" not in app.config:
            app.config["OAREPO_PERMISSIONS_PRESETS"] = {}

        for k in ext_config.OAREPO_VOCABULARIES_PERMISSIONS_PRESETS:
            if k not in app.config["OAREPO_PERMISSIONS_PRESETS"]:
                app.config["OAREPO_PERMISSIONS_PRESETS"][
                    k
                ] = ext_config.OAREPO_VOCABULARIES_PERMISSIONS_PRESETS[k]

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.service = app.config["VOCABULARY_TYPE_SERVICE"](
            config=app.config["VOCABULARY_TYPE_SERVICE_CONFIG"](),
        )

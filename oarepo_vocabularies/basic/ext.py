from oarepo_vocabularies.basic import config as config


class OARepoVocabulariesBasicExt(object):
    """extension."""

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
        app.extensions["oarepo-vocabularies-basic"] = self

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.service = app.config["BASIC_SERVICE_CLASS"](
            config=app.config["BASIC_SERVICE_CONFIG"](),
        )
        self.resource = app.config["BASIC_RESOURCE_CLASS"](
            service=self.service,
            config=app.config["BASIC_RESOURCE_CONFIG"](),
        )

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault("BASIC_RESOURCE_CONFIG", config.BASIC_RESOURCE_CONFIG)
        app.config.setdefault("BASIC_RESOURCE_CLASS", config.BASIC_RESOURCE_CLASS)
        app.config.setdefault("BASIC_SERVICE_CONFIG", config.BASIC_SERVICE_CONFIG)
        app.config.setdefault("BASIC_SERVICE_CLASS", config.BASIC_SERVICE_CLASS)

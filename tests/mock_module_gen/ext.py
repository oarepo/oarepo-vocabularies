from mock_module_gen import config as config


class MockModuleGenExt(object):
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
        app.extensions["mock_module_gen"] = self

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.service = app.config["MOCK_MODULE_GEN_SERVICE_CLASS"](
            config=app.config["MOCK_MODULE_GEN_SERVICE_CONFIG"](),
        )
        self.resource = app.config["MOCK_MODULE_GEN_RESOURCE_CLASS"](
            service=self.service,
            config=app.config["MOCK_MODULE_GEN_RESOURCE_CONFIG"](),
        )

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "MOCK_MODULE_GEN_RESOURCE_CONFIG", config.MOCK_MODULE_GEN_RESOURCE_CONFIG
        )
        app.config.setdefault(
            "MOCK_MODULE_GEN_RESOURCE_CLASS", config.MOCK_MODULE_GEN_RESOURCE_CLASS
        )
        app.config.setdefault(
            "MOCK_MODULE_GEN_SERVICE_CONFIG", config.MOCK_MODULE_GEN_SERVICE_CONFIG
        )
        app.config.setdefault(
            "MOCK_MODULE_GEN_SERVICE_CLASS", config.MOCK_MODULE_GEN_SERVICE_CLASS
        )

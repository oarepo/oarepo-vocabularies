from . import config

class OARepoVocabulariesExt(object):
    """extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["oarepo-vocabularies"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("OAREPO_VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))

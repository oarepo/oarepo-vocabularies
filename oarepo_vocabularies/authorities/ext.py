from functools import lru_cache

from invenio_base.utils import obj_or_import_string


class OARepoVocabulariesAuthorities(object):
    """OARepo extension of Invenio-Vocabularies for authorities."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        self.app = app
        if app:
            self.init_app(app)

    @lru_cache(maxsize=None)
    def get_authority_api(self, vocabulary_type: str):
        vocabularies_metadata = self.app.config["INVENIO_VOCABULARY_TYPE_METADATA"]
        authority = vocabularies_metadata[vocabulary_type].get("authority", None)
        if authority:
            return obj_or_import_string(authority)()

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.init_resource(app)
        app.extensions["oarepo-vocabularies-authorities"] = self

    def init_config(self, app):
        from . import ext_config

        app.config.setdefault(
            "OAREPO_VOCABULARIES_AUTHORITIES",
            ext_config.OAREPO_VOCABULARIES_AUTHORITIES,
        )
        app.config.setdefault(
            "OAREPO_VOCABULARIES_AUTHORITIES_CONFIG",
            ext_config.OAREPO_VOCABULARIES_AUTHORITIES_CONFIG,
        )

    def init_resource(self, app):
        """Initialize resources."""
        self.resource = obj_or_import_string(
            app.config["OAREPO_VOCABULARIES_AUTHORITIES"]
        )(config=app.config["OAREPO_VOCABULARIES_AUTHORITIES_CONFIG"]())

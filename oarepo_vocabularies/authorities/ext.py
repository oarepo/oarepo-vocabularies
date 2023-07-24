from functools import lru_cache

from invenio_base.utils import obj_or_import_string


class OARepoVocabulariesAuthorities(object):
    """OARepo extension of Invenio-Vocabularies for authorities."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        if app:
            self.init_app(app)

    @lru_cache(maxsize=None)
    def auth_getter(self, app, vocabulary_type: str):
        vocabularies_metadata = app.config["INVENIO_VOCABULARY_TYPE_METADATA"]
        authority_section = vocabularies_metadata[vocabulary_type].get(
            "authority", None
        )

        return (
            authority_section.get(obj_or_import_string("getter"), None)
            if authority_section
            else None
        )

    def init_app(self, app):
        """Flask application initialization."""
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

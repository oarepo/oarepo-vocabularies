from flask import current_app
from invenio_records_resources.services import Link, LinksTemplate
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.records import ServiceSchemaWrapper
from invenio_vocabularies.records.models import VocabularyType


class VocabulariesService(Service):
    """Vocabulary service."""

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self):
        """Item links template."""
        return LinksTemplate(
            self.config.vocabularies_listing_item,
        )

    def search(self, identity):
        """Search for vocabulary entries."""
        self.require_permission(identity, "list_vocabularies")

        vocabulary_types = VocabularyType.query.all()

        config_vocab_types = current_app.config["INVENIO_VOCABULARY_TYPE_METADATA"]

        # Extend database data with configuration data.
        results = []
        for db_vocab_type in vocabulary_types:
            result = {"id": db_vocab_type.id, "pid_type": db_vocab_type.pid_type}

            if db_vocab_type.id in config_vocab_types:
                for k, v in config_vocab_types[db_vocab_type.id].items():
                    result[k] = v

            results.append(result)

        return self.result_list(
            self,
            identity,
            results,
            links_tpl=LinksTemplate({"self": Link("{+api}/vocabularies")}),
            links_item_tpl=self.links_item_tpl,
        )

from flask import current_app
from invenio_records_resources.services import Link, LinksTemplate, RecordServiceConfig
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.records import ServiceSchemaWrapper
from invenio_search import current_search_client
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyType


class VocabularyTypeService(Service):
    """Vocabulary types service."""

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
        """Search for vocabulary types entries."""
        self.require_permission(identity, "list_vocabularies")

        vocabulary_types = VocabularyType.query.all()

        config_vocab_types = current_app.config["INVENIO_VOCABULARY_TYPE_METADATA"]

        count_terms_agg = self._vocabulary_statistics()

        # Extend database data with configuration & aggregation data.
        results = []
        for db_vocab_type in vocabulary_types:
            result = {
                "id": db_vocab_type.id,
                "pid_type": db_vocab_type.pid_type,
                "count": count_terms_agg.get(db_vocab_type.id, 0),
            }

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

    def _vocabulary_statistics(self):
        config: RecordServiceConfig = current_service.config
        search_opts = config.search

        search = search_opts.search_cls(
            using=current_search_client,
            index=config.record_cls.index.search_alias,
        )

        search.aggs.bucket("vocabularies", {"terms": {"field": "type.id", "size": 100}})

        search_result = search.execute()
        buckets = search_result.aggs.to_dict()["vocabularies"]["buckets"]

        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}

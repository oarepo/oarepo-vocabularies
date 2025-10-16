#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Services for vocabularies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from invenio_records_resources.services import (
    EndpointLink,
    LinksTemplate,
    RecordServiceConfig,
)
from invenio_records_resources.services.records import ServiceSchemaWrapper
from invenio_search import current_search_client
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.service import VocabularyTypeService as InvenioVocabularyTypeService

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordList


class VocabularyTypeService(InvenioVocabularyTypeService):
    """Vocabulary types service."""

    @property
    def schema(self) -> ServiceSchemaWrapper:
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self) -> LinksTemplate:
        """Item links template."""
        return LinksTemplate(
            self.config.vocabularies_listing_item,
        )

    def search(self, identity: Identity, params: dict | None = None) -> RecordList:  # noqa: ARG002 # type: ignore[override]
        """Search for vocabulary types entries."""
        self.require_permission(identity, "list_vocabularies")

        vocabulary_types = VocabularyType.query.all()  # type: ignore[attr-defined]

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
                result.update(dict(config_vocab_types[db_vocab_type.id].items()))

            results.append(result)

        return self.result_list(
            self,
            identity,
            results,
            links_tpl=LinksTemplate(
                {
                    "self": EndpointLink(
                        "oarepo_vocabulary_type.list",
                    )
                }
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def _vocabulary_statistics(self) -> dict:
        """Get vocabularies number of documents using aggregations."""
        config: RecordServiceConfig = current_service.config
        search_opts = config.search

        search = search_opts.search_cls(
            using=current_search_client,
            index=config.record_cls.index.search_alias,  # type: ignore[attr-defined]
        )

        search.aggs.bucket("vocabularies", {"terms": {"field": "type.id", "size": 100}})

        search_result = search.execute()
        buckets = search_result.aggs.to_dict()["vocabularies"]["buckets"]

        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}

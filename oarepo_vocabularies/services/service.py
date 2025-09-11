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

from typing import TYPE_CHECKING, Any

from flask import current_app
from invenio_records_resources.services import (
    EndpointLink,
    LinksTemplate,
    RecordServiceConfig,
)
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.records import ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from invenio_search import current_search_client
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services import (
    VocabulariesService as InvenioVocabulariesService,
)

from oarepo_vocabularies.proxies import current_oarepo_vocabularies

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services.records.results import RecordItem, RecordList
    from invenio_records_resources.services.uow import UnitOfWork


class VocabularyTypeService(Service):
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

    def search(self, identity: Identity, params: dict | None = None) -> RecordList:  # noqa: ARG002
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
            index=config.record_cls.index.search_alias,
        )

        search.aggs.bucket("vocabularies", {"terms": {"field": "type.id", "size": 100}})

        search_result = search.execute()
        buckets = search_result.aggs.to_dict()["vocabularies"]["buckets"]

        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}


class VocabulariesService(InvenioVocabulariesService):
    """Vocabulary service supporting specialized services per vocabulary type."""

    def search(
        self,
        identity: Identity,
        params: dict | None = None,
        search_preference: Any = None,
        type: str | None = None,  # noqa: A002
        **kwargs: Any,
    ) -> RecordList:
        """Search for vocabulary entries."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.search(
                identity=identity,
                params=params,
                search_preference=search_preference,
                **kwargs,
            )
        return super().search(
            identity=identity,
            params=params,
            search_preference=search_preference,
            type=type,
            **kwargs,
        )

    def search_many(
        self,
        identity: Identity,
        params: dict,
        search_preference: Any | None = None,
        type: str | None = None,  # noqa: A002
        **kwargs: Any,
    ) -> RecordList:
        """Search for vocabulary entries."""
        # we are skipping Invenio vocabularies service here and calling
        # explicitly its parent class. The reason is that invenio vocabs
        # always filter the search by a single vocabulary type. The search_many
        # use case is an optimization where we want to fetch multiple items
        # from multiple vocabulary types in a single query.

        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.search(
                identity=identity,
                params=params,
                search_preference=search_preference,
                **kwargs,
            )
        return super(InvenioVocabulariesService, self).search(identity, params)

    def read_all(
        self,
        identity: Identity,
        fields: list[str],
        type: str,  # noqa: A002
        cache: bool = True,
        extra_filter: str = "",
        **kwargs: Any,
    ) -> RecordList:
        """Search for records matching the querystring."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.read_all(
                identity=identity,
                fields=fields,
                cache=cache,
                extra_filter=extra_filter,
                **kwargs,
            )
        return super().read_all(
            identity=identity,
            fields=fields,
            type=type,
            cache=cache,
            extra_filter=extra_filter,
            **kwargs,
        )

    def read_many(
        self,
        identity: Identity,
        type: str,  # noqa: A002
        ids: list[str],
        fields: list[str] | None = None,
        **kwargs: Any,
    ) -> RecordList:
        """Search for records matching the querystring filtered by ids."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.read_many(identity=identity, ids=ids, fields=fields, **kwargs)
        return super().read_many(identity=identity, type=type, ids=ids, fields=fields, **kwargs)

    @unit_of_work()
    def create(
        self, identity: Identity, data: dict, uow: UnitOfWork | None = None, expand: bool = False, **kwargs: Any
    ) -> RecordItem:
        """Public API to create a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(data.get("type"))
        if specialized_service:
            data.pop("type")
            return specialized_service.create(identity=identity, data=data, uow=uow, expand=expand, **kwargs)
        return super().create(identity=identity, data=data, uow=uow, expand=expand, **kwargs)

    def read(
        self, identity: Identity, id_: tuple[str, str], expand: bool = False, action: str = "read", **kwargs: Any
    ) -> RecordItem:
        """Retrieve a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.read(identity=identity, id_=id_[1], expand=expand, action=action, **kwargs)
        return super().read(identity=identity, id_=id_, expand=expand, action=action, **kwargs)

    def exists(self, identity: Identity, id_: tuple[str, str], **kwargs: Any) -> bool:
        """Check if the record exists and user has permission."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.exists(identity=identity, id_=id_[1], **kwargs)
        return super().exists(identity=identity, id_=id_, **kwargs)

    def _create(  # noqa: PLR0913
        self,
        record_cls: Record,
        identity: Identity,
        data: dict,
        raise_errors: bool = True,
        uow: UnitOfWork | None = None,
        expand: bool = False,
        **kwargs: Any,
    ) -> RecordItem:
        """Create a record."""
        return super()._create(
            record_cls,
            identity,
            data,
            raise_errors=raise_errors,
            uow=uow,
            expand=expand,
            **kwargs,
        )

    @unit_of_work()
    def update(  # noqa: PLR0913
        self,
        identity: Identity,
        id_: tuple[str, str],
        data: dict,
        revision_id: int | None = None,
        uow: UnitOfWork | None = None,
        expand: bool = False,
        **kwargs: Any,
    ) -> RecordItem:
        """Replace a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.update(
                identity=identity,
                id_=id_[1],
                data=data,
                revision_id=revision_id,
                uow=uow,
                expand=expand,
                **kwargs,
            )

        return super().update(
            identity,
            id_,
            data,
            revision_id=revision_id,
            uow=uow,
            expand=expand,
            **kwargs,
        )

    @unit_of_work()
    def delete(
        self,
        identity: Identity,
        id_: tuple[str, str],
        revision_id: int | None = None,
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> bool:
        """Delete a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.delete(
                identity=identity,
                id_=id_[1],
                revision_id=revision_id,
                uow=uow,
                **kwargs,
            )
        return super().delete(identity, id_, revision_id=revision_id, uow=uow, **kwargs)

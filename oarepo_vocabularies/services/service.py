import functools

from flask import current_app
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services import Link, LinksTemplate, RecordServiceConfig
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records import ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from invenio_search import current_search_client
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services import (
    VocabulariesService as InvenioVocabulariesService,
)

from oarepo_vocabularies.proxies import current_oarepo_vocabularies


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


class VocabulariesService(InvenioVocabulariesService):

    def search(
        self, identity, params=None, search_preference=None, type=None, **kwargs
    ):
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.search(
                identity=identity, params=params, search_preference=search_preference, **kwargs)
        return super().search(identity=identity, params=params,
                              search_preference=search_preference, type=type, **kwargs)

    def search_many(self, identity, params):
        # we are skipping Invenio vocabularies service here and calling
        # explicitly its parent class. The reason is that invenio vocabs
        # always filter the search by a single vocabulary type. The search_many
        # use case is an optimization where we want to fetch multiple items
        # from multiple vocabulary types in a single query.
        return super(InvenioVocabulariesService, self).search(identity, params)

    def read_all(self, identity, fields, type, cache=True, extra_filter="", **kwargs):
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.read_all(identity=identity,
                                                fields=fields,
                                                cache=cache,
                                                extra_filter=extra_filter,
                                                **kwargs)
        return super().read_all(identity=identity, fields=fields, type=type,
                                cache=cache, extra_filter=extra_filter, **kwargs)

    def read_many(self, identity, type, ids, fields=None, **kwargs):
        """Search for records matching the querystring filtered by ids."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(type)
        if specialized_service:
            return specialized_service.read_many(identity=identity, ids=ids, fields=fields, **kwargs)
        return super().read_many(identity=identity, type=type, ids=ids, fields=fields, **kwargs)

    @unit_of_work()
    def create(self, identity, data, uow=None, expand=False, **kwargs):
        specialized_service = current_oarepo_vocabularies.get_specialized_service(data.get("type"))
        if specialized_service:
            data.pop("type")
            return specialized_service.create(identity=identity, data=data, uow=uow, expand=expand, **kwargs)
        return super().create(identity=identity, data=data, uow=uow, expand=expand, **kwargs)

    def read(self, identity, id_, expand=False, action="read", **kwargs):
        """Retrieve a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.read(identity=identity, id_=id_[1],
                                            expand=expand, action=action, **kwargs)
        return super().read(identity=identity, id_=id_, expand=expand, action=action, **kwargs)

    def exists(self, identity, id_, **kwargs):
        """Check if the record exists and user has permission."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.exists(identity=identity, id_=id_[1], **kwargs)
        return super().exists(identity=identity, id_=id_, **kwargs)

    def _create(
        self,
        record_cls,
        identity,
        data,
        raise_errors=True,
        uow=None,
        expand=False,
        **kwargs,
    ):
        vocabulary_type = data.get("type", None)
        if vocabulary_type:
            self.require_permission(
                identity, self.get_vocabulary_permission_name("create", vocabulary_type)
            )
        else:
            return PermissionDeniedError(
                f"Permission denied on creating vocabulary without type."
            )

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
    def update(
        self, identity, id_, data, revision_id=None, uow=None, expand=False, **kwargs
    ):
        """Replace a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.update(identity=identity, id_=id_[1],
                                              data=data, revision_id=revision_id,
                                              uow=uow, expand=expand, **kwargs)

        record = self.record_cls.pid.resolve(id_)
        self.require_permission(
            identity,
            self.get_vocabulary_permission_name("update", record.type.id),
            record=record,
            data=data,
            **kwargs
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
    def delete(self, identity, id_, revision_id=None, uow=None, **kwargs):
        """Delete a record."""
        specialized_service = current_oarepo_vocabularies.get_specialized_service(id_[0])
        if specialized_service:
            return specialized_service.delete(
                identity=identity,
                id_=id_[1],
                revision_id=revision_id,
                uow=uow, **kwargs)


        record = self.record_cls.pid.resolve(id_)
        self.require_permission(
            identity,
            self.get_vocabulary_permission_name("delete", record.type.id),
            record=record,
        )
        return super().delete(identity, id_, revision_id=revision_id, uow=uow, **kwargs)

    def get_vocabulary_permission_name(self, operation, vocabulary_type):
        vocabulary_type = vocabulary_type.replace("-", "_")
        return f"{operation}_{vocabulary_type}"



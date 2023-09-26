import inspect

from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from oarepo_runtime.relations.errors import (
    InvalidRelationError,
    MultipleInvalidRelationErrors,
)
from oarepo_runtime.relations.mapping import RelationsMapping

from oarepo_vocabularies.authorities.proxies import authorities
from oarepo_vocabularies.authorities.service import AuthorityService


class AuthorityComponent(ServiceComponent):
    def create(self, identity, data=None, record=None, errors=None, **kwargs):
        self.lookup_and_store_authority_records(record)

    def update(self, identity, data=None, record=None, **kwargs):
        self.lookup_and_store_authority_records(record)

    def lookup_and_store_authority_records(self, record):
        # get the relations system field
        relations_fields = inspect.getmembers(
            record, lambda x: isinstance(x, RelationsMapping)
        )

        for relations_field_name, relations in relations_fields:
            # iterate all vocabularies there, check that the item exists
            for fld_name in relations:
                fld = getattr(relations, fld_name)
                try:
                    pid_context = fld.field.pid_field
                except:
                    continue
                if not isinstance(pid_context, VocabularyPIDFieldContext):
                    continue
                try:
                    fld.validate(raise_first_exception=False)
                except MultipleInvalidRelationErrors as e:
                    # check if there is an authority service
                    vocabulary_type = pid_context._type_id
                    authority_service = authorities.get_authority_api(vocabulary_type)

                    if not authority_service:
                        raise

                    # if so, for each record store the authority record
                    for err in e.errors:
                        self.resolve_and_store_authority_record(
                            fld,
                            result=err[0],
                            error=err[1],
                            authority_service=authority_service,
                            vocabulary_type=vocabulary_type,
                        )

                    # and run again validate to populate this record with de-referenced value
                    fld.validate()

    def resolve_and_store_authority_record(
        self,
        fld,
        *,
        result,
        error,
        authority_service: AuthorityService,
        vocabulary_type,
    ):
        with db.session.begin_nested():
            value = result.value or {}
            if "id" not in value:
                raise InvalidRelationError(
                    f"'id' not found in relation value {value}",
                    related_id=None,
                    location=result.path,
                )
            item_id = value["id"]
            try:
                fetched_item = authority_service.get(item_id, uow=self.uow, value=value)
            except Exception as e:
                raise InvalidRelationError(
                    f"External authority failed: {e}",
                    related_id=item_id,
                    location=result.path,
                ) from e

            rec = vocabulary_service.create(
                system_identity, {**fetched_item, "type": vocabulary_type}, uow=self.uow
            )
            # possible optimization - put the created vocab item to the cache on fld.cache
            # in the form: ('<pid-type>', '<id>'): {created record}
            # so that it is not fetched again from the database

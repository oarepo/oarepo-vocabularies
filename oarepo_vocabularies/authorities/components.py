from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_vocabularies.proxies import current_service as vocabulary_service
from oarepo_runtime.services.relations.errors import (
    InvalidRelationError,
    MultipleInvalidRelationErrors,
)

from oarepo_vocabularies.authorities.providers import AuthorityProvider
from oarepo_vocabularies.authorities.proxies import authorities
from oarepo_vocabularies.records.api import find_vocabulary_relations


class AuthorityComponent(ServiceComponent):
    def create(self, identity, data=None, record=None, errors=None, **kwargs):
        self.lookup_and_store_authority_records(identity, record)

    def update(self, identity, data=None, record=None, **kwargs):
        self.lookup_and_store_authority_records(identity, record)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        self.lookup_and_store_authority_records(identity, record)

    def lookup_and_store_authority_records(self, identity, record):
        for found_vocabulary in find_vocabulary_relations(record):
            try:
                found_vocabulary.field.validate(raise_first_exception=False)
            except MultipleInvalidRelationErrors as e:
                authority_service = authorities.get_authority_api(
                    found_vocabulary.vocabulary_type
                )

                if not authority_service:
                    # no authority service => can not resolve validation errors
                    raise

                # if so, for each record store the authority record
                for err in e.errors:
                    self.resolve_and_store_authority_record(
                        identity,
                        found_vocabulary.field,
                        result=err[0],
                        error=err[1],
                        authority_service=authority_service,
                        vocabulary_type=found_vocabulary.vocabulary_type,
                    )

                # and run again validate to populate this record with de-referenced value
                found_vocabulary.field.validate()

    def resolve_and_store_authority_record(
        self,
        identity,
        fld,
        *,
        result,
        error,
        authority_service: AuthorityProvider,
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
                vocabulary_service.read(system_identity, (vocabulary_type, item_id))
                return
            except:
                pass
            try:
                fetched_item = authority_service.get(
                    identity, item_id, uow=self.uow, value=value
                )
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

import abc
import marshmallow as ma

from types import SimpleNamespace
from marshmallow import fields as ma_fields, validate
from oarepo_vocabularies.authorities.clients import RORClientV2
from oarepo_vocabularies.authorities.results import RORListResultV2, RORItemV2
from invenio_records_resources.services import Link, LinksTemplate, pagination_links
from invenio_records_resources.services.records import ServiceSchemaWrapper


class AuthorityService(abc.ABC):
    @abc.abstractmethod
    def search(self, identity, params, **kwargs):
        """
        Search the external authority service by the given text query and return
        page & size with the data. The returned structure must be the same as Invenio
        vocabulary listing, that is:
        ```
        {
            'hits': {
                'total': <number of results>,
                'hits': [
                    {'id': 1, title: {'en': ...}, ...},
                    {'id': 1, title: {'en': ...}, ...},
                ]
            },
            'links': {
                'self': ...,
                'next': ...
            }
        }
        ```
        """

    @abc.abstractmethod
    def get(self, identity, item_id, *, uow, value, **kwargs):
        """
        Gets vocabulary item by id. Returns the item as JSON or KeyError if the item could not be found.
        @param item_id  value['id']
        @param uow      actual unit of work (if you need to create something inside the db, do it inside this uow)
        @param value    the value passed from the client
        """


class RORNameSchemaV2(ma.Schema):
    value = ma_fields.String(required=True)
    types = ma_fields.List(
        ma_fields.String(
            validate=validate.OneOf(["acronym", "alias", "label", "ror_display"])
        ),
    )
    lang = ma_fields.String()


class RORLinkSchema(ma.Schema):
    type = ma_fields.String(
        required=True, validate=validate.OneOf(["website", "wikipedia"])
    )
    value = ma_fields.String(required=True)


class RORGeoDetailsSchema(ma.Schema):
    name = ma_fields.String(required=True)
    country_name = ma_fields.String()
    country_code = ma_fields.String()

class RORLocationSchema(ma.Schema):
    geonames_details = ma_fields.Nested(lambda: RORGeoDetailsSchema())


class RORMetadataSchemaV2(ma.Schema):
    id = ma_fields.String(required=True)
    names = ma_fields.List(ma_fields.Nested(lambda: RORNameSchemaV2()))
    types = ma_fields.List(
        ma_fields.String(
            validate=validate.OneOf(
                [
                    "education",
                    "funder",
                    "healthcare",
                    "company",
                    "archive",
                    "nonprofit",
                    "government",
                    "facility",
                    "other",
                ]
            ),
        ),
    )
    links = ma_fields.List(ma_fields.Nested(lambda: RORLinkSchema()))
    locations = ma_fields.List(ma_fields.Nested(lambda: RORLocationSchema()))

    class Meta:
        unknown = ma.INCLUDE


class RORAuthorityServiceV2(AuthorityService):

    config = SimpleNamespace(
        schema=RORMetadataSchemaV2,
        parent_vocabulary_type="institutions",
        permission_policy_cls=None,
        result_list_cls=RORListResultV2,
        result_item_cls=RORItemV2,
        ror_client_cls=RORClientV2,
        links_item_tpl={
            "self": Link(
                "{+api}/vocabularies/{type}/authoritative/{id}",
                vars=lambda record, vars: vars.update({"id": record.id}),
            )
        },
    )

    def __init__(self, url=None, testing=False, **kwargs):
        self.ror_client = self.config.ror_client_cls(url, testing, **kwargs)

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def links_item_tpl(self):
        """Item links template."""
        return LinksTemplate(
            self.config.links_item_tpl,
            context={"type": self.config.parent_vocabulary_type},
        )

    def search(self, identity, params, **kwargs):
        # TODO(mesemus): check permissions (e.g. only authenticated can query authority)?
        params = params or {}

        results = self.ror_client.quick_search(params, **kwargs)
        results["hits"] = results.pop("items")

        return self.result_list(
            self,
            identity,
            results,
            params=params,
            links_tpl=LinksTemplate(
                {
                    **pagination_links(
                        "{+api}/vocabularies/{type}/authoritative{?args*}"
                    ),
                },
                context={"args": params, "type": self.config.parent_vocabulary_type},
            ),
            links_item_tpl=self.links_item_tpl,
        ).to_dict()

    def get(self, identity, item_id, **kwargs):
        record = self.ror_client.get_record(item_id, **kwargs)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        ).to_dict()

    def result_list(self, *args, **kwargs):
        """Create a new instance of the resource list.

        A resource list is an instantiated object representing a grouping
        of Resource units. Sometimes this group has additional data making
        a simple iterable of resource units inappropriate. It is what a
        Resource list methods transact in and therefore what
        a Service must provide.
        """
        return self.config.result_list_cls(*args, **kwargs)

    def result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit.

        A resource unit is an instantiated object representing one unit
        of a Resource. It is what a Resource transacts in and therefore
        what a Service must provide.
        """
        return self.config.result_item_cls(*args, **kwargs)

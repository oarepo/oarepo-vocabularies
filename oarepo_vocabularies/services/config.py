import marshmallow as ma
from invenio_records_resources.services import Link, pagination_links
from invenio_records_resources.services.base import ServiceListResult
from invenio_vocabularies.services import VocabulariesServiceConfig
from oarepo_runtime.config.service import PermissionsPresetsConfigMixin

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.components.hierarchy import HierarchyComponent
from oarepo_vocabularies.services.schema import VocabularySchema
from oarepo_vocabularies.services.search import VocabularySearchOptions

from .components.scanning_order import ScanningOrderComponent
from .permissions import PermissionPolicy


class VocabularyMetadataSchema(ma.Schema):
    class Meta:
        unknown = ma.INCLUDE


class VocabularyMetadataList(ServiceListResult):
    def __init__(
        self,
        service,
        identity,
        results,
        links_tpl=None,
        links_item_tpl=None,
    ):
        """Constructor.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the search results
        """
        self._identity = identity
        self._results = results
        self._service = service
        self._links_tpl = links_tpl
        self._links_item_tpl = links_item_tpl

    def to_dict(self):
        hits = list(self._results)

        for hit in hits:
            if self._links_item_tpl:
                hit["links"] = self._links_item_tpl.expand(self._identity, hit)

        res = {
            "hits": {
                "hits": hits,
                "total": len(hits),
            }
        }

        if self._links_tpl:
            res["links"] = self._links_tpl.expand(self._identity, None)

        return res


class VocabularyTypeServiceConfig(PermissionsPresetsConfigMixin):
    service_id = "vocabulary_type"
    schema = VocabularyMetadataSchema
    result_list_cls = VocabularyMetadataList

    PERMISSIONS_PRESETS = ["vocabularies"]

    vocabularies_listing_item = {
        "self": Link(
            "{+api}/vocabularies/{id}",
            vars=lambda vocab_type, vars: vars.update({"id": vocab_type["id"]}),
        ),
        "self_html": Link(
            "{+ui}/vocabularies/{id}",
            vars=lambda vocab_type, vars: vars.update({"id": vocab_type["id"]}),
        ),
    }


class VocabulariesConfig(VocabulariesServiceConfig):
    record_cls = Vocabulary
    schema = VocabularySchema
    search = VocabularySearchOptions
    components = [
        *VocabulariesServiceConfig.components,
        HierarchyComponent,
        ScanningOrderComponent,
    ]
    permission_policy_cls = PermissionPolicy

    url_prefix = "/vocabularies/"

    links_item = {
        **VocabulariesServiceConfig.links_item,
        "self_html": Link(
            "{+ui}/vocabularies/{type}/{id}",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
        ),
        "vocabulary": Link(
            "{+api}/vocabularies/{type}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                }
            ),
        ),
        "vocabulary_html": Link(
            "{+ui}/vocabularies/{type}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                }
            ),
        ),
        "parent": Link(
            "{+api}/vocabularies/{type}/{parent}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "parent": record.get("hierarchy", {}).get("parent"),
                }
            ),
            when=lambda obj, ctx: bool(obj.get("hierarchy", {}).get("parent")),
        ),
        "parent_html": Link(
            "{+ui}/vocabularies/{type}/{parent}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "parent": record.get("hierarchy", {}).get("parent"),
                }
            ),
            when=lambda obj, ctx: bool(obj.get("hierarchy", {}).get("parent")),
        ),
        "children": Link(
            "{+api}/vocabularies/{type}?h-parent={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
        "children_html": Link(
            "{+ui}/vocabularies/{type}?h-parent={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
        "descendants": Link(
            "{+api}/vocabularies/{type}?h-ancestor={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
        "descendants_html": Link(
            "{+ui}/vocabularies/{type}?h-ancestor={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
    }

    links_search = {
        **pagination_links("{+api}/vocabularies/{type}{?args*}"),
        **{
            f"{k}_html": v
            for k, v in pagination_links("{+ui}/vocabularies/{type}{?args*}").items()
        },
    }

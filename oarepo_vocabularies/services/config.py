import marshmallow as ma
from invenio_records_resources.services import Link, pagination_links
from invenio_records_resources.services.base import ServiceListResult
from invenio_records_resources.services.records.links import EndpointLink
from invenio_vocabularies.services import VocabulariesServiceConfig

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.schema import VocabularySchema
from oarepo_vocabularies.services.search import VocabularySearchOptions

from .components.keep_vocabulary_id import KeepVocabularyIdComponent
from .components.scanning_order import ScanningOrderComponent
from .permissions import VocabulariesPermissionPolicy


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


class VocabularyTypeServiceConfig:
    service_id = "vocabulary_type"
    schema = VocabularyMetadataSchema
    result_list_cls = VocabularyMetadataList

    PERMISSIONS_PRESETS = ["vocabularies"]
    permission_policy_cls = VocabulariesPermissionPolicy
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
        KeepVocabularyIdComponent,
        *VocabulariesServiceConfig.components,
        # HierarchyComponent, TODO: remove
        ScanningOrderComponent,
    ]

    PERMISSIONS_PRESETS = ["vocabularies"]
    # PERMISSIONS_PRESETS_CONFIG_KEY = "VOCABULARIES_PERMISSIONS_PRESETS"

    url_prefix = "/vocabularies/"

    links_item = {
        **VocabulariesServiceConfig.links_item,
        "self_html": EndpointLink(
            "oarepo_vocabularies_ui.detail",
            vars=lambda record, vars: vars.update(
                {
                    "pid_value": record.pid.pid_value,
                    "vocabulary_type": record.type.id,
                }
            ),
            params=["vocabulary_type", "pid_value"],
        ),
        "vocabulary": EndpointLink(
            "vocabularies.search",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                }
            ),
            params=["type"],
        ),
        "vocabulary_html": EndpointLink(
            "oarepo_vocabularies_ui.search",
            vars=lambda record, vars: vars.update(
                {
                    "vocabulary_type": record.type.id,
                }
            ),
            params=["vocabulary_type"],
        ),
        "parent": EndpointLink(
            "vocabularies.read",
            vars=lambda record, vars: vars.update(
                {"type": record.type.id, "pid_value": record.hierarchy.parent_id}
            ),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),
            params=["type", "pid_value"],
        ),
        "parent_html": EndpointLink(
            "oarepo_vocabularies_ui.detail",
            vars=lambda record, vars: vars.update(
                {
                    "vocabulary_type": record.type.id,
                    "pid_value": record.hierarchy.parent_id,
                }
            ),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),
            params=["vocabulary_type", "pid_value"],
        ),
        "children": EndpointLink(
            "vocabularies.search",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                    "args": {"h-parent": record.pid.pid_value},
                }
            ),
            params=["type"],
        ),
        "children_html": EndpointLink(
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                    "args": {"h-parent": record.pid.pid_value},
                },
            ),
            params=["type"],
        ),
        "descendants_html": EndpointLink(
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                    "args": {"h-ancestor": record.pid.pid_value},
                }
            ),
            params=["type"],
        ),
    }

    links_search = {
        **pagination_links("{+api}/vocabularies/{type}{?args*}"),
        **{
            f"{k}_html": v
            for k, v in pagination_links("{+ui}/vocabularies/{type}{?args*}").items()
        },
    }

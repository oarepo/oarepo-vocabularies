#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import marshmallow as ma
from invenio_records_resources.services import pagination_endpoint_links
from invenio_records_resources.services.base import ServiceListResult
from invenio_records_resources.services.records.links import EndpointLink
from invenio_vocabularies.services import VocabulariesServiceConfig
from invenio_vocabularies.services.permissions import PermissionPolicy
from oarepo_runtime.services.records.links import pagination_endpoint_links_html

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.schema import VocabularySchema
from oarepo_vocabularies.services.search import VocabularySearchOptions

from .components.keep_vocabulary_id import KeepVocabularyIdComponent
from .components.scanning_order import ScanningOrderComponent


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

    permission_policy_cls = PermissionPolicy
    vocabularies_listing_item = {
        "self": EndpointLink(
            "vocabularies.search",
            vars=lambda vocab_type, vars: vars.update({"type": vocab_type["id"]}),
            params=["type"],
        ),
        "self_html": EndpointLink(
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda vocab_type, vars: vars.update({"type": vocab_type["id"]}),
            params=["type"],
        ),
    }


class VocabulariesConfig(VocabulariesServiceConfig):
    record_cls = Vocabulary
    schema = VocabularySchema
    search = VocabularySearchOptions
    components = [
        KeepVocabularyIdComponent,
        *VocabulariesServiceConfig.components,
        ScanningOrderComponent,
    ]

    PERMISSIONS_PRESETS = ["vocabularies"]

    url_prefix = "/vocabularies/"

    links_item = {
        **VocabulariesServiceConfig.links_item,
        "self_html": EndpointLink(
            "oarepo_vocabularies_ui.detail",
            vars=lambda record, vars: vars.update(
                {
                    "pid_value": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
            params=["type", "pid_value"],
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
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                }
            ),
            params=["type"],
        ),
        "parent": EndpointLink(
            "vocabularies.read",
            vars=lambda record, vars: vars.update({"type": record.type.id, "pid_value": record.hierarchy.parent_id}),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),
            params=["type", "pid_value"],
        ),
        "parent_html": EndpointLink(
            "oarepo_vocabularies_ui.detail",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "pid_value": record.hierarchy.parent_id,
                }
            ),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),
            params=["type", "pid_value"],
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
        "descendants": EndpointLink(
            "vocabularies.search",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                    "args": {"h-ancestor": record.pid.pid_value},
                }
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
        **pagination_endpoint_links("vocabularies.search", params=["type"]),
        **pagination_endpoint_links_html("oarepo_vocabularies_ui.search_without_slash", params=["type"]),
    }

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Configuration for vocabularies service."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, cast

import marshmallow as ma
from flask import current_app
from invenio_base.utils import obj_or_import_string
from invenio_records_resources.services import pagination_endpoint_links
from invenio_records_resources.services.base import ServiceListResult
from invenio_records_resources.services.base.links import EndpointLink
from invenio_vocabularies.services import VocabulariesServiceConfig
from invenio_vocabularies.services.config import VocabularyTypesServiceConfig as InvenioVocabularyTypesServiceConfig
from invenio_vocabularies.services.permissions import PermissionPolicy
from oarepo_runtime.services.records.links import pagination_endpoint_links_html

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.schema import VocabularySchema
from oarepo_vocabularies.services.search import VocabularySearchOptions

from .components.keep_vocabulary_id import KeepVocabularyIdComponent
from .components.scanning_order import ScanningOrderComponent

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_principal import Identity
    from invenio_records_permissions import RecordPermissionPolicy
    from invenio_records_resources.services.base import Service
    from invenio_records_resources.services.base.links import LinksTemplate
    from invenio_records_resources.services.records.components import ServiceComponent


class VocabularyMetadataSchema(ma.Schema):
    """Schema for vocabulary metadata records."""

    class Meta:
        """Meta class for the schema."""

        unknown = ma.INCLUDE


class VocabularyMetadataList(ServiceListResult):
    """List of vocabulary metadata records."""

    def __init__(
        self,
        service: Service,
        identity: Identity,
        results: Any,
        links_tpl: LinksTemplate | None = None,
        links_item_tpl: LinksTemplate | None = None,
    ):
        """Init the vocabulary metadata list.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the search results
        """
        self._identity = identity
        self._results = results
        self._service = service
        self._links_tpl = links_tpl
        self._links_item_tpl = links_item_tpl

    def to_dict(self) -> dict:
        """Convert the result to a dictionary."""
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


class PermissionPolicyFactory:
    """Factory for permission policy to enable dynamic permissions policies."""

    @cached_property
    def current_permission_policy_class(self) -> type[RecordPermissionPolicy]:
        """Get the current permission policy class from the app config."""
        return cast(
            "type[RecordPermissionPolicy]",
            obj_or_import_string(current_app.config.get("VOCABULARIES_PERMISSIONS_POLICY", PermissionPolicy)),
        )

    def __call__(self, *args: Any, **kwargs: Any) -> RecordPermissionPolicy:
        """Create the permission policy instance in runtime."""
        return self.current_permission_policy_class(*args, **kwargs)


class VocabularyTypeServiceConfig(InvenioVocabularyTypesServiceConfig):
    """Vocabulary types service configuration."""

    schema = VocabularyMetadataSchema
    result_list_cls = VocabularyMetadataList

    # TODO: Invenio vocabularies service uses vocabularies config as a class, not as an instance
    # As we can not have class property, we simulate it with a callable class
    permission_policy_cls = PermissionPolicyFactory()  # type: ignore[type-arg]
    vocabularies_listing_item: ClassVar[dict[str, EndpointLink]] = {
        "self": EndpointLink(
            "vocabularies.search",
            vars=lambda vocab_type, vars_: vars_.update({"type": vocab_type["id"]}),
            params=["type"],
        ),
        "self_html": EndpointLink(
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda vocab_type, vars_: vars_.update({"type": vocab_type["id"]}),
            params=["type"],
        ),
    }


class VocabulariesConfig(VocabulariesServiceConfig):
    """Vocabulary service configuration."""

    record_cls = Vocabulary
    schema = VocabularySchema
    search = VocabularySearchOptions  # type: ignore[type-arg]
    components: ClassVar[list[type[ServiceComponent]]] = [  # type: ignore[override]
        KeepVocabularyIdComponent,
        *VocabulariesServiceConfig.components,
        ScanningOrderComponent,
    ]
    # TODO: Invenio vocabularies service uses vocabularies config as a class, not as an instance
    # As we can not have class property, we simulate it with a callable class
    permission_policy_cls = PermissionPolicyFactory()  # type: ignore[type-arg]

    url_prefix = "/vocabularies/"
    links_item: ClassVar[Mapping[str, EndpointLink]] = {  # type: ignore[override]
        "self": EndpointLink(
            "vocabularies.read",
            vars=lambda record, _vars: _vars.update(
                {
                    "pid_value": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
            params=["type", "pid_value"],
        ),
        "self_html": EndpointLink(
            "oarepo_vocabularies_ui.record_detail",
            vars=lambda record, vars_: vars_.update(
                {
                    "pid_value": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
            params=["type", "pid_value"],
        ),
        "vocabulary": EndpointLink(
            "vocabularies.search",
            vars=lambda record, vars_: vars_.update(
                {
                    "type": record.type.id,
                }
            ),
            params=["type"],
        ),
        "vocabulary_html": EndpointLink(
            "oarepo_vocabularies_ui.search_without_slash",
            vars=lambda record, vars_: vars_.update(
                {
                    "type": record.type.id,
                }
            ),
            params=["type"],
        ),
        "parent": EndpointLink(
            "vocabularies.read",
            vars=lambda record, vars_: vars_.update({"type": record.type.id, "pid_value": record.hierarchy.parent_id}),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),  # noqa: ARG005
            params=["type", "pid_value"],
        ),
        "parent_html": EndpointLink(
            "oarepo_vocabularies_ui.record_detail",
            vars=lambda record, vars_: vars_.update(
                {
                    "type": record.type.id,
                    "pid_value": record.hierarchy.parent_id,
                }
            ),
            when=lambda obj, ctx: bool(obj.hierarchy.parent_id),  # noqa: ARG005
            params=["type", "pid_value"],
        ),
        "children": EndpointLink(
            "vocabularies.search",
            vars=lambda record, vars_: vars_.update(
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
            vars=lambda record, vars_: vars_.update(
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
            vars=lambda record, vars_: vars_.update(
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
            vars=lambda record, vars_: vars_.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                    "args": {"h-ancestor": record.pid.pid_value},
                }
            ),
            params=["type"],
        ),
    }

    links_search: ClassVar[Mapping[str, EndpointLink]] = {  # type: ignore[override]
        **pagination_endpoint_links("vocabularies.search", params=["type"]),
        **pagination_endpoint_links_html("oarepo_vocabularies_ui.search_without_slash", params=["type"]),
    }

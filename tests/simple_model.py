#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import marshmallow as ma
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.models import RecordMetadata
from invenio_records.systemfields.relations.field import RelationsField
from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField, PIDField
from invenio_records_resources.records.systemfields.pid import PIDFieldContext
from invenio_records_resources.records.systemfields.relations import (  # z invenio-records-resources
    PIDRelation,
)
from invenio_records_resources.services import (
    RecordLink,
    RecordService,
    RecordServiceConfig,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.api import Model
from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent


class ModelRecordIdProvider(RecordIdProviderV2):
    """Record identifier provider."""

    pid_type = "rec"


class ModelRecord(Record):
    """Record model."""

    index = IndexField("test_record")
    model_cls = RecordMetadata
    pid = PIDField(
        provider=ModelRecordIdProvider, context_cls=PIDFieldContext, create=True
    )
    relations = RelationsField(
        authority=PIDRelation(
            "authority",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("authority"),
        ),
        ror_authority=PIDRelation(
            "ror_authority",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("ror-authority"),
        ),
        lng=PIDRelation(
            "lng",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
        ),
        creator=PIDRelation(
            "creator",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("creator"),
        ),
        award=PIDRelation(
            "award",
            keys=["id", "title"],
            pid_field=Vocabulary.pid.with_type_ctx("award"),
        ),
    )


class ModelPermissionPolicy(RecordPermissionPolicy):
    """Permission policy for records."""

    can_create = [AnyUser(), SystemProcess()]  # noqa: RUF012
    can_update = [AnyUser(), SystemProcess()]  # noqa: RUF012
    can_search = [AnyUser(), SystemProcess()]  # noqa: RUF012
    can_read = [AnyUser(), SystemProcess()]  # noqa: RUF012


class ModelSchema(ma.Schema):
    """Model schema."""

    title = ma.fields.String()
    authority = ma.fields.Raw()  # just a simulation ...
    ror_authority = ma.fields.Raw(data_key="ror-authority")
    creator = ma.fields.Raw()
    award = ma.fields.Raw()

    class Meta:
        """Meta."""

        unknown = ma.INCLUDE


class ModelServiceConfig(RecordServiceConfig):
    """Record service config."""

    record_cls = ModelRecord
    permission_policy_cls = ModelPermissionPolicy
    schema = ModelSchema
    components = [DataComponent]  # noqa: RUF012

    url_prefix = "/simple-model"

    @property
    def links_item(self):
        """Item links config."""
        return {
            "self": RecordLink(f"{{+api}}{self.url_prefix}/{{id}}"),
            "ui": RecordLink(f"{{+ui}}{self.url_prefix}/{{id}}"),
        }


class ModelService(RecordService):
    """Record service."""


class ModelUISerializer(MarshmallowSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=ModelSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )


class ModelUIResourceConfig(RecordsUIResourceConfig):
    """Record UI resource config."""

    api_service = "simple_model"  # must be something included in oarepo, as oarepo is used in tests

    blueprint_name = "simple_model"
    url_prefix = "/simple-model"
    ui_serializer_class = ModelUISerializer
    templates = {  # noqa: RUF012
        **RecordsUIResourceConfig.templates,
        "detail": "TestDetail",
        "search": "TestSearch",
    }
    model_name = "SimpleModel"
    components = [BabelComponent, PermissionsComponent]  # noqa: RUF012


class ModelUIResource(RecordsUIResource):
    """Record UI resource."""


simple_model = Model(
    code="simple_model",
    name=_("Simple Model"),
    version="1.0.0",
    service="simple_model",
    service_config=ModelServiceConfig(),
    record=ModelRecord,
    resource_config=ModelUIResourceConfig(),
    ui_model={
        "name": "SimpleModel",
        "templates": {"detail": "TestDetail", "search": "TestSearch"},
    },
)

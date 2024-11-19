import marshmallow as ma
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.models import RecordMetadata
from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField, PIDField
from invenio_records_resources.records.systemfields.pid import PIDFieldContext
from invenio_records_resources.services import (
    RecordLink,
    RecordService,
    RecordServiceConfig,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.records.relations import PIDRelation, RelationsField
from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent

from oarepo_vocabularies.authorities.components import AuthorityComponent


class ModelRecordIdProvider(RecordIdProviderV2):
    pid_type = "rec"


class ModelRecord(Record):
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
        ) 

    )

class ModelPermissionPolicy(RecordPermissionPolicy):
    can_create = [AnyUser(), SystemProcess()]
    can_update = [AnyUser(), SystemProcess()]
    can_search = [AnyUser(), SystemProcess()]
    can_read = [AnyUser(), SystemProcess()]


class ModelSchema(ma.Schema):
    title = ma.fields.String()
    authority = ma.fields.Raw()  # just a simulation ...
    ror_authority = ma.fields.Raw(data_key="ror-authority")
    creator = ma.fields.Raw()

    class Meta:
        unknown = ma.INCLUDE


class ModelServiceConfig(RecordServiceConfig):
    record_cls = ModelRecord
    permission_policy_cls = ModelPermissionPolicy
    schema = ModelSchema
    components = [DataComponent, AuthorityComponent]

    url_prefix = "/simple-model"

    @property
    def links_item(self):
        return {
            "self": RecordLink("{+api}%s/{id}" % self.url_prefix),
            "ui": RecordLink("{+ui}%s/{id}" % self.url_prefix),
        }


class ModelService(RecordService):
    pass


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
    api_service = "simple_model"  # must be something included in oarepo, as oarepo is used in tests

    blueprint_name = "simple_model"
    url_prefix = "/simple-model"
    ui_serializer_class = ModelUISerializer
    templates = {
        **RecordsUIResourceConfig.templates,
        "detail": "TestDetail",
        "search": "TestSearch",
    }

    components = [BabelComponent, PermissionsComponent]


class ModelUIResource(RecordsUIResource):
    pass

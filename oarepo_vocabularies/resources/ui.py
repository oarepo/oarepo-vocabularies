from functools import partial

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.services.custom_fields import CustomFieldsSchemaUI
from invenio_vocabularies.resources.serializer import (
    VocabularyL10NItemSchema as InvenioVocabularyL10NItemSchema,
)

from oarepo_vocabularies.services.type_ui_schema import VocabularyTypeUISchema
import marshmallow


class VocabularyTypeUIJSONSerializer(MarshmallowSerializer):
    """Vocabulary type UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=VocabularyTypeUISchema,
            list_schema_cls=BaseListSchema,
            # schema_context={"object_key": "ui"},
        )

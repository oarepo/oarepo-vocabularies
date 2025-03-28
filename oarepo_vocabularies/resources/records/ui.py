from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from oarepo_vocabularies.resources.config import VocabularySchemaSelector


class VocabularyUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=VocabularySchemaSelector,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )

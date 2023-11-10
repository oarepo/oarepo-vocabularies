from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from oarepo_vocabularies.services.type_ui_schema import VocabularyTypeUISchema


class VocabularyTypeUIJSONSerializer(LocalizedUIJSONSerializer):
    """Vocabulary type UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=VocabularyTypeUISchema,
            list_schema_cls=BaseListSchema,
            # schema_context={"object_key": "ui"},
        )

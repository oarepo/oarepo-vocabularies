from functools import partial

from invenio_records_resources.services.custom_fields import CustomFieldsSchema
from invenio_vocabularies.services.schema import (
    VocabularySchema as InvenioVocabularySchema,
)
from marshmallow_utils.fields import NestedAttribute
from oarepo_runtime.cf import InlinedCustomFieldsSchemaMixin


class VocabularySchema(InlinedCustomFieldsSchemaMixin, InvenioVocabularySchema):
    CUSTOM_FIELDS_VAR = "OAREPO_VOCABULARIES_CUSTOM_CF"
    hierarchy = NestedAttribute(
        partial(CustomFieldsSchema, fields_var="OAREPO_VOCABULARIES_HIERARCHY_CF")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

from flask_resources import ResponseHandler
from invenio_vocabularies.resources import (
    VocabularyTypeResourceConfig as InvenioVocabularyTypeResourceConfig,
)

from oarepo_vocabularies.resources.ui import VocabularyTypeUIJSONSerializer


class VocabularyTypeResourceConfig(InvenioVocabularyTypeResourceConfig):
    response_handlers = {
        **InvenioVocabularyTypeResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            VocabularyTypeUIJSONSerializer()
        ),
    }

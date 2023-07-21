from flask_resources.context import ResourceRequestCtx

from oarepo_vocabularies.ui.resources.config import InvenioVocabulariesUIResourceConfig
from oarepo_vocabularies.ui.resources.resource import InvenioVocabulariesUIResource


def test_empty_record(app):
    config = InvenioVocabulariesUIResourceConfig()
    resource = InvenioVocabulariesUIResource(config=config)
    ctx = ResourceRequestCtx(config)
    ctx.view_args = {"vocabulary_type": "test"}
    with ctx:
        assert resource.empty_record(resource_requestctx=ctx) == {
            "blah": None,
            "created": None,
            "description": None,
            "hierarchy": None,
            "hint": None,
            "icon": None,
            "id": None,
            "links": None,
            "nonpreferredLabels": [None],
            "props": None,
            "relatedURI": None,
            "revision_id": None,
            "tags": [None],
            "title": None,
            "type": "test",
            "updated": None,
        }

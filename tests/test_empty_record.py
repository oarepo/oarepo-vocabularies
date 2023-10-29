from flask_resources.context import ResourceRequestCtx


def test_empty_record(app, vocabularies_ui_resource, vocabularies_ui_resource_config):
    ctx = ResourceRequestCtx(vocabularies_ui_resource_config)
    ctx.view_args = {"vocabulary_type": "test"}
    with ctx:
        assert vocabularies_ui_resource.empty_record(resource_requestctx=ctx) == {
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
            "tags": [],
            "title": None,
            "type": "test",
            "updated": None,
        }

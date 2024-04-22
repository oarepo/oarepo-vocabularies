from flask_resources.context import ResourceRequestCtx


def test_empty_record(app, vocabularies_ui_resource, vocabularies_ui_resource_config):
    ctx = ResourceRequestCtx(vocabularies_ui_resource_config)
    ctx.view_args = {"vocabulary_type": "test"}
    with ctx:
        assert vocabularies_ui_resource.empty_record(resource_requestctx=ctx) == {
            "blah": "",
            "created": None,
            "description": {},
            "hierarchy": {
                "ancestors": [],
                "ancestors_or_self": [],
                "level": None,
                "parent": "",
                "title": [],
                'leaf': None,
            },
            "hint": {},
            "icon": "",
            "id": "",
            "links": None,
            "nonpreferredLabels": [],
            "props": {},
            "relatedURI": {},
            "revision_id": None,
            "tags": [],
            "title": {},
            "type": "test",
            "updated": None,
        }

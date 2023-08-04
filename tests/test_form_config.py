def test_form_config(
    app,
    db,
    cache,
    vocab_cf,
    lang_type,
    lang_data_many,
    vocabularies_ui_resource,
    identity,
    search_clear,
):
    fc = vocabularies_ui_resource.config.form_config(identity=identity)

    assert fc == dict(
        links=dict(),
        custom_fields={"ui": {}},
    )

    vocabularies_ui_resource.run_components(
        "form_config",
        form_config=fc,
        layout="",
        resource=vocabularies_ui_resource,
        record={},
        data={},
        args={},
        view_args={},
        identity=identity,
        extra_context={},
    )

    assert fc == dict(
        languages=[
            # NOTE: "English" is a fallback title,
            # as we don't set lang title in test fixture
            {"value": "fr", "text": "English"},
            {"value": "tr", "text": "English"},
            {"value": "gr", "text": "English"},
            {"value": "ger", "text": "English"},
            {"value": "es", "text": "English"},
        ],
        links=dict(),
        custom_fields={"ui": {}},
    )

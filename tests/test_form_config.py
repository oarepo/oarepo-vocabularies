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
    assert vocabularies_ui_resource.config.form_config(identity=identity) == dict(
        current_locale="en",
        locales=[
            {
                "value": "en",
                "text": "English",
            },
            {"value": "da", "text": "dansk"},
        ],
        default_locale="en",
        identity=identity,
        languages={
            "all": [
                # NOTE: "English" is fallback title, 
                # as we don't set lang title in test fixture
                {"value": "fr", "text": "English"},
                {"value": "tr", "text": "English"},
                {"value": "gr", "text": "English"},
                {"value": "ger", "text": "English"},
                {"value": "es", "text": "English"},
            ],
            "common": [
                {"value": "es", "text": "English"},
            ],
        },
        links=dict(),
        custom_fields={"ui": {}},
    )

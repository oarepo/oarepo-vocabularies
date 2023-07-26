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
                {"value": "en", "text": "English"},
                {"value": "cs", "text": "čeština"},
            ],
            "common": [
                {"value": "en", "text": "English"},
                {"value": "cs", "text": "čeština"},
            ],
        },
        links=dict(),
        custom_fields={"ui": {}},
    )

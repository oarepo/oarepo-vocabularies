def test_form_config(
    app,
    db,
    cache,
    vocab_cf,
    lang_type,
    lang_data_many,
    vocabularies_ui_resource,
    identity,
    search_clear
):
    assert vocabularies_ui_resource.config.form_config(identity=identity) == dict(
        current_locale="en",
        locales=[
            # TODO: not sure why current_i18.get_locales() puts English twice here
            {"value": "en", "text": "English"},
            {"value": "en", "text": "English"},
            {"value": "cs", "text": "čeština"},
        ],
        default_locale="en",
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

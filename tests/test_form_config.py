from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_form_config(
    app, db, cache, lang_type, lang_data_many, vocabularies_ui_resource, identity
):
    assert vocabularies_ui_resource.config.form_config(identity) == dict(
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

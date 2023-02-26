from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_extra_cf(app, db, cache, lang_type, vocab_cf):
    lang_object = vocab_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
            "blah": "Hello",
        },
    )

    assert lang_object.data["blah"] == "Hello"

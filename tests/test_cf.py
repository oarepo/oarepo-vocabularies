from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_extra_cf(app, db, cache, lang_type, vocab_cf, search_clear):
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


def test_czech_sort(
    app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear
):
    data = client.get(
        "/api/vocabularies/languages?sort=title", headers=[("Accept-Language", "cs")]
    ).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina",
        "Angličtina (A pro řazení)",
        "Angličtina (UK)",
        "Angličtina (US)",
    ]


def test_czech_suggest(
    app, db, cache, lang_type, vocab_cf, sample_records, client, search_clear
):
    data = client.get(
        "/api/vocabularies/languages?suggest=%C5%99azen%C3%AD",
        headers=[("Accept-Language", "cs")],
    ).json
    titles = [d["title"]["cs"] for d in data["hits"]["hits"]]
    assert titles == [
        "Angličtina (A pro řazení)",
    ]

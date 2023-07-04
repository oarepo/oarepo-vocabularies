from oarepo_vocabularies.proxies import current_type_service as vocabulary_type_service


def test_counts(
    app,
    app_config,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
):
    search_result = vocabulary_type_service.search(identity)
    results = search_result.to_dict()

    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = [hit for hit in hits if hit["id"] == "languages"][0]
    assert hits_languages["count"] == 5

    hits_licences = [hit for hit in hits if hit["id"] == "licences"][0]
    assert hits_licences["count"] == 0

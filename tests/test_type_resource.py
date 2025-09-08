#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
def test_resource_get(
    app,
    client,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
):
    resp = client.get("/api/vocabularies/").json

    results = resp
    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0


def test_accept_header(
    app,
    client,
    db,
    identity,
    vocab_cf,
    lang_data_many,
    empty_licences,
    search_clear,
):
    invenio_json_header = "application/vnd.inveniordm.v1+json"
    resp = client.get("/api/vocabularies/", headers={"accept": invenio_json_header}).json

    results = resp
    assert results["hits"]["total"] == 2
    hits = results["hits"]["hits"]

    hits_languages = next(hit for hit in hits if hit["id"] == "languages")
    assert hits_languages["count"] == 5

    hits_licences = next(hit for hit in hits if hit["id"] == "licences")
    assert hits_licences["count"] == 0


def test_ui_endpoint_without_slash(app, client, db, identity, vocab_cf, lang_data_many, fake_manifest):
    resp_1 = client.get("/vocabularies/")
    resp_2 = client.get("/vocabularies")

    assert resp_1.data == resp_2.data

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import pytest


@pytest.mark.skip(reason="Needs fixtures loading")
def test_serialization_api(app, db, cache, vocab_cf, reset_babel, search_clear, cache_clear, identity, client):
    # load_fixtures here...

    with client.get("/api/vocabularies/languages") as response:
        assert response.status_code == 200
        hits = response.json["hits"]["hits"]
        assert len(hits) == 2

        assert hits[0]["title"]["cs"] == "Čeština"
        assert hits[0]["props"]["alpha3CodeNative"] == "ces"
        assert hits[0]["relatedURI"]["url"] == "https://cs.com"

        assert hits[1]["title"]["en"] == "English"
        assert hits[1]["props"]["alpha3CodeNative"] == "eng"
        assert hits[1]["relatedURI"]["url"] == "https://en.com"


@pytest.mark.skip(reason="Needs fixtures loading")
def test_serialization_api_vnd(app, db, cache, vocab_cf, reset_babel, search_clear, cache_clear, identity, client):
    # load_fixtures here...

    with client.get(
        "/api/vocabularies/languages",
        headers={
            "Accept": "application/vnd.inveniordm.v1+json",
            "Accept-Language": "cs",
        },
    ) as response:
        assert response.status_code == 200
        hits = response.json["hits"]["hits"]
        assert len(hits) == 2

        assert hits[1]["title"] == "Čeština"
        assert hits[1]["props"]["alpha3CodeNative"] == "ces"
        assert hits[1]["relatedURI"]["url"] == "https://cs.com"

        assert hits[0]["title"] == "Angličtina"
        assert hits[0]["props"]["alpha3CodeNative"] == "eng"
        assert hits[0]["relatedURI"]["url"] == "https://en.com"

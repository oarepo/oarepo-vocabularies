#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.names.api import Name
from invenio_vocabularies.proxies import current_service as vocab_service

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.service import VocabulariesService

vocab_service: VocabulariesService


def test_names_crud(app, db, cache, vocab_cf, search_clear):
    rec = vocab_service.create(
        identity=system_identity,
        data={
            "type": "names",
            "id": "test",
            "given_name": "Mirek",
            "family_name": "Svoboda",
        },
    )

    full_rec = {
        "id": "test",
        "links": {
            "self": "https://127.0.0.1:5000/api/names/test",
            "self_html": "https://127.0.0.1:5000/vocabularies/names/test",
        },
        "revision_id": 3,
        "name": "Svoboda, Mirek",
        "given_name": "Mirek",
        "family_name": "Svoboda",
    }
    assert full_rec.items() <= rec.data.items()

    current_service_registry.get("names").indexer.refresh()

    all_names = list(vocab_service.search(system_identity, type="names").hits)
    assert len(all_names) == 1
    assert full_rec.items() <= all_names[0].items()

    vocab_service.update(
        identity=system_identity,
        id_=("names", "test"),
        data={
            "given_name": "Jana",
            "family_name": "Novotna",
        },
    )

    current_service_registry.get("names").indexer.refresh()

    rec = vocab_service.read(system_identity, ("names", "test"))
    assert {
        "given_name": "Jana",
        "family_name": "Novotna",
    }.items() <= rec.data.items()


@pytest.mark.skip(reason="Needs fixtures loading")
def test_names_fixtures_load(app, db, cache, vocab_cf, search_clear):
    # load fixtures here...

    names_service = current_service_registry.get("names")
    names_service.indexer.refresh()
    correct = {
        "given_name": "Mirek",
        "family_name": "Svoboda",
    }
    # through vocab service
    assert correct.items() <= vocab_service.read(system_identity, ("names", "test")).data.items()

    # through names service
    assert correct.items() <= names_service.read(system_identity, "test").data.items()


@pytest.mark.skip(reason="Needs fixtures loading")
def test_serialization_api_vnd(app, db, cache, vocab_cf, reset_babel, search_clear, cache_clear, identity, client):
    # load fixtures here...

    with client.get(
        "/api/vocabularies/names",
        headers={
            "Accept": "application/vnd.inveniordm.v1+json",
            "Accept-Language": "cs",
        },
    ) as response:
        assert response.status_code == 200
        hits = response.json["hits"]["hits"]
        assert len(hits) == 1

        assert hits[0]["family_name"] == "Svoboda"
        assert hits[0]["given_name"] == "Mirek"
        assert "type" not in hits[0]


@pytest.mark.skip(reason="Needs fixtures loading")
def test_specialized_service_record_resolver(app, db, cache, vocab_cf, search_clear):
    # load fixtures here...

    resolved = Vocabulary.pid.resolve(("names", "test"))
    assert isinstance(resolved, Name)
    assert resolved["given_name"] == "Mirek"
    assert resolved["family_name"] == "Svoboda"

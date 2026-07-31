#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import re


def remove_ws(x):
    return re.sub(r"\s+", "", x)


def test_uidetail(
    vocabularies_ui_resource,
    identity,
    logged_in_client,
    fake_manifest,
    app,
    clear_vocabulary_permissions,
    db,
    cache,
    search_clear,
    client,
    vocab_cf,
    lang_data_many,
):
    detail_page = logged_in_client.get("/vocabularies/languages/fr")
    assert detail_page.status_code == 200


def test_vocabulary_content_negotiation_redirects_for_api_accept_header(
    vocabularies_ui_resource,
    identity,
    logged_in_client,
    fake_manifest,
    app,
    clear_vocabulary_permissions,
    db,
    cache,
    search_clear,
    client,
    vocab_cf,
    lang_data_many,
):
    resp = logged_in_client.get(
        "/vocabularies/languages/eng",
        headers={"Accept": "application/json"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/api/vocabularies/languages/eng" in resp.location

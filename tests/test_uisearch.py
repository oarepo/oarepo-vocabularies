# SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations


def test_search(
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
    search = logged_in_client.get("/vocabularies/languages/")
    assert search.status_code == 200
    search_without_slash = logged_in_client.get("/vocabularies/languages")
    assert search_without_slash.status_code == 302
    assert search_without_slash.headers["Location"] == "/vocabularies/languages/"

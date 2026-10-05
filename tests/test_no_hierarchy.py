# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_simple_lang(app, db, cache, lang_type, lang_data, vocab_cf, clear_vocabulary_permissions):
    lang_object = vocab_service.create(system_identity, lang_data)
    assert lang_object.data["hierarchy"] == {
        "level": 1,
        "titles": [{"cs": "Angličtina", "da": "Engelsk", "en": "English"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
        "parent": None,
    }

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def test_simple_lang(app, db, cache, lang_type, lang_data, vocab_cf):
    lang_object = vocab_service.create(system_identity, lang_data)
    assert lang_object.data["hierarchy"] == {
        "level": 1,
        "titles": [{"cs": "Angličtina", "da": "Engelsk", "en": "English"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
        "parent": None,
    }

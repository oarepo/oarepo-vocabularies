#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.records.models import VocabularyHierarchy


def test_extra_cf_relations(app, db, cache, lang_type, vocab_cf, search_clear):
    parent_data = {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello",
    }

    child_data = {
        "id": "eng-us",
        "title": {"en": "English (US)", "da": "Engelsk (US)"},
        "type": {"id": "languages", "pid_type": "lng"},
        "blah": "Hello in american",
        "parent": {"id": "eng"},
    }

    parent_rec = Vocabulary.create(data=parent_data)
    Vocabulary.pid.create(parent_rec)
    parent_rec.commit()
    db.session.commit()

    assert parent_rec.hierarchy.to_dict() == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": True,
        "parent": None,
    }

    child_rec = Vocabulary.create(data=child_data)
    Vocabulary.pid.create(child_rec)
    child_rec.commit()
    db.session.commit()

    parent_uuid = parent_rec.id
    child_uuid = child_rec.id

    # check DB table
    entries = VocabularyHierarchy.query.filter_by(
        id=child_uuid, parent_id=parent_uuid
    ).all()

    assert len(entries) == 1

    assert child_rec.hierarchy.to_dict() == {
        "level": 2,
        "titles": [
            {"en": "English (US)", "da": "Engelsk (US)"},
            {"en": "English", "da": "Engelsk"},
        ],
        "ancestors": ["eng"],
        "ancestors_or_self": ["eng-us", "eng"],
        "leaf": True,
        "parent": "eng",
    }

    # check the updated hierarchy
    parent_rec = Vocabulary.get_record(parent_rec.id)
    assert parent_rec.hierarchy.to_dict() == {
        "level": 1,
        "titles": [{"en": "English", "da": "Engelsk"}],
        "ancestors": [],
        "ancestors_or_self": ["eng"],
        "leaf": False,
        "parent": None,
    }

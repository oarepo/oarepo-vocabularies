#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import tempfile
from pathlib import Path

import pytest
import yaml
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.api import Vocabulary


def read_yaml(fp):
    with open(fp) as f:
        ret = list(yaml.safe_load_all(f))
        if len(ret) == 1:
            return ret[0]
        return ret


@pytest.mark.skip(reason="Needs fixtures loading")
def test_import_export_hierarchy_data(app, db, cache, vocab_cf):
    # load fixtures here...

    Vocabulary.index.refresh()

    assert current_service.read(system_identity, ("languages", "en")).data["id"] == "en"
    assert current_service.read(system_identity, ("languages", "en.US")).data["hierarchy"]["ancestors"] == ["en"]

    with tempfile.TemporaryDirectory() as d:
        # export
        d = Path(d)
        assert read_yaml(d / "catalogue.yaml") == {
            "vocabulary-languages": [
                {"pid_type": "lng", "vocabulary": "languages", "writer": "vocabulary"},
                {"source": "vocabulary-languages.yaml"},
            ]
        }
        assert set(x["title"]["en"] for x in read_yaml(d / "vocabulary-languages.yaml")) == {"English", "English (US)"}

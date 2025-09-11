#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

import pytest
from invenio_vocabularies.records.api import Vocabulary


@pytest.mark.skip(reason="Needs fixtures loading")
def test_complex_import_export(app, db, cache, vocab_cf):
    # load fixtures here...

    Vocabulary.index.refresh()

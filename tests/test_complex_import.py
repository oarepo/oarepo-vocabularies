# SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest
from invenio_vocabularies.records.api import Vocabulary


@pytest.mark.skip(reason="Needs fixtures loading")
def test_complex_import_export(app, db, cache, vocab_cf):
    # load fixtures here...

    Vocabulary.index.refresh()

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

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocab_service


def remove_ws(x):
    return re.sub(r"\s+", "", x)


def test_uidetail(client, app, db, cache, lang_type, lang_data, vocab_cf, fake_manifest):
    vocab_service.create(system_identity, lang_data)
    detail_page = client.get("/vocabularies/languages/eng")
    assert detail_page.status_code == 200
    assert remove_ws(""""props": {\n    "akey": "avalue"\n  }""") in remove_ws(detail_page.text)

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from datetime import UTC, datetime
from typing import Any

import marshmallow

from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField


class VocabularyCacheItem:
    last_modified: datetime
    items: dict[str, Any]

    def __init__(self):
        self.last_modified = datetime.fromtimestamp(0, UTC)
        self.items = {}


class DepositI18nHierarchySchema(marshmallow.Schema):
    title = marshmallow.fields.List(VocabularyI18nStrUIField())
    ancestors = marshmallow.fields.List(marshmallow.fields.String())

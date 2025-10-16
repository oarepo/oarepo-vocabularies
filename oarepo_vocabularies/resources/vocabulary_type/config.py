#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Configuration for vocabulary type resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from flask_resources import ResponseHandler
from invenio_vocabularies.resources import (
    VocabularyTypeResourceConfig as InvenioVocabularyTypeResourceConfig,
)

from oarepo_vocabularies.resources.ui import VocabularyTypeUIJSONSerializer

if TYPE_CHECKING:
    from collections.abc import Mapping


class VocabularyTypeResourceConfig(InvenioVocabularyTypeResourceConfig):
    """Configuration for vocabulary type resource."""

    blueprint_name = "oarepo_vocabulary_type"

    response_handlers: ClassVar[Mapping[str, ResponseHandler]] = {  # type: ignore[override]
        **InvenioVocabularyTypeResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(VocabularyTypeUIJSONSerializer()),
    }

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_resources import ResponseHandler
from invenio_vocabularies.resources import (
    VocabularyTypeResourceConfig as InvenioVocabularyTypeResourceConfig,
)

from oarepo_vocabularies.resources.ui import VocabularyTypeUIJSONSerializer


class VocabularyTypeResourceConfig(InvenioVocabularyTypeResourceConfig):
    blueprint_name = "oarepo_vocabulary_type"

    response_handlers = {
        **InvenioVocabularyTypeResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": ResponseHandler(VocabularyTypeUIJSONSerializer()),
    }

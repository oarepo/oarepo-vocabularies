#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_records_resources.services.records.components import ServiceComponent


class KeepVocabularyIdComponent(ServiceComponent):
    def update(self, identity, data=None, record=None, **kwargs):
        if "id" not in data:
            data["id"] = record["id"]

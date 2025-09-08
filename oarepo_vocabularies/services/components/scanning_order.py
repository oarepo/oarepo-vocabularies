#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_records_resources.services.records.components import ServiceComponent


class ScanningOrderComponent(ServiceComponent):
    def scan(self, identity, search, params):
        if params.get("preserve_order"):
            return search.params(preserve_order=True)
        return search

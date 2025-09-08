#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from invenio_base.utils import obj_or_import_string
from oarepo_ui.resources import UIResourceConfig


class VocabularyTypeUIResourceConfig(UIResourceConfig):
    url_prefix = "/vocabularies"
    blueprint_name = "vocabulary_type_app"
    ui_serializer_class = "oarepo_vocabularies.resources.ui.VocabularyTypeUIJSONSerializer"
    api_service = "vocabulary_type"
    layout = "vocabulary"

    templates = {"list": "oarepo_vocabularies_ui.VocabulariesList"}

    routes = {"list": "/"}

    @property
    def ui_serializer(self):
        return obj_or_import_string(self.ui_serializer_class)()

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabulary Type UI Resource config."""

from __future__ import annotations

from typing import Any, ClassVar

from invenio_base.utils import obj_or_import_string
from oarepo_ui.resources import UIResourceConfig


class VocabularyTypeUIResourceConfig(UIResourceConfig):
    """Vocabulary Type UI Resource config."""

    url_prefix = "/vocabularies"
    blueprint_name = "vocabulary_type_app"
    ui_serializer_class = "oarepo_vocabularies.resources.ui.VocabularyTypeUIJSONSerializer"
    api_service = "vocabulary_type"
    layout = "vocabulary"

    templates: ClassVar[dict[str, str]] = {"list": "oarepo_vocabularies_ui.VocabulariesList"}

    routes: ClassVar[dict[str, str]] = {"list": "/"}

    @property
    def ui_serializer(self) -> Any:
        """Return an instance of the serializer class."""
        ui_serializer_cls = obj_or_import_string(self.ui_serializer_class)
        if ui_serializer_cls is None:
            raise RuntimeError("UI serializer class not found.")
        return ui_serializer_cls()

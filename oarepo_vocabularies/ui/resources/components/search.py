#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resource component for vocabulary search."""

from __future__ import annotations

from typing import Any

from oarepo_ui.resources.components import UIResourceComponent


class VocabularySearchComponent(UIResourceComponent):
    """Process the data before the search page is rendered."""

    def before_ui_search(self, *, search_options: dict, view_args: dict, **kwargs: Any) -> None:  # noqa: ARG002
        """Process the data before the search page is rendered."""
        search_options["headers"] = {"Accept": "application/json"}

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI Resources components."""

from __future__ import annotations

import inspect
import json
from typing import TYPE_CHECKING, Any, ClassVar

from flask import current_app
from invenio_records import Record
from invenio_vocabularies.proxies import current_service
from oarepo_ui.resources.components import UIResourceComponent

from oarepo_vocabularies.records.api import find_vocabulary_relations

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services.records.results import RecordItem


class DepositVocabularyOptionsComponent(UIResourceComponent):
    """Component uses in deposit form of normal records.

    For small vocabularies, it provides their values so that they might be displayed in, for example, a combo.
    """

    always_included_vocabularies: ClassVar[list[str]] = []

    def form_config(  # noqa: PLR0913  too many arguments
        self,
        *,
        api_record: RecordItem,
        record: dict,  # noqa: ARG002
        identity: Identity,
        form_config: dict,
        ui_links: dict,  # noqa: ARG002
        extra_context: dict,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Add vocabularies to the form config as in.

        Example:
        "vocabularies": {
            "languages": {
              "definition": {...} # from INVENIO_VOCABULARY_TYPE_METADATA
              "all": [{"value": "...", "text": "..."}],
              "featured": [{"value": "...", "text": "..."}]
            },
            "bigVocabulary: {
                "definition": {...} # from INVENIO_VOCABULARY_TYPE_METADATA
                "url": "..."
            },
          }

        The vocabularies which should be handled this way are configured
        inside invenio.cfg:

        ```
        INVENIO_VOCABULARY_TYPE_METADATA = {
            "languages": {
                "dump_options": True,
                # more configuration here
            }
        ```

        """
        if not isinstance(api_record, Record):
            record_cls = self.resource.api_service.config.record_cls  # type: ignore[attr-defined]
            api_record = record_cls({})

        form_config.setdefault("vocabularies", {})

        vocabulary_config = current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {})

        used_vocabularies = self._get_used_vocabularies(api_record)

        (
            vocabularies_to_prefetch,
            form_config_vocabularies,
        ) = self.create_form_config_vocabularies(vocabulary_config, used_vocabularies=used_vocabularies)

        form_config["vocabularies"] = form_config_vocabularies
        self._prefetch_vocabularies_to_form_config(form_config_vocabularies, vocabularies_to_prefetch, identity)

    def _get_used_vocabularies(self, api_record: RecordItem) -> list[str]:
        used_vocabularies = [vocab_field.vocabulary_type for vocab_field in find_vocabulary_relations(api_record)]
        for v in self.always_included_vocabularies:
            if v not in used_vocabularies:
                used_vocabularies.append(v)
        return used_vocabularies

    def _prefetch_vocabularies_to_form_config(
        self,
        form_config_vocabularies: dict,
        vocabularies_to_prefetch: list[str],
        identity: Identity,
    ) -> None:
        """Prefetch vocabularies to form config."""
        for vocabulary_to_fetch in vocabularies_to_prefetch:
            # search instead of read_all also provides links, because template links are passed to result list init
            hits = current_service.search(identity, {}, type=vocabulary_to_fetch).hits
            for hit in hits:
                item = {"value": hit.pop("id"), "element_type": "leaf" if hit["hierarchy"]["leaf"] else "parent", **hit}
                form_config_vocabularies[vocabulary_to_fetch]["all"].append(item)
                if "featured" in item.get("tags", []):
                    form_config_vocabularies[vocabulary_to_fetch]["featured"].append(item)

    @staticmethod
    def create_form_config_vocabularies(
        vocabulary_config: dict,
        used_vocabularies: list[str],
    ) -> tuple[list[str], dict]:
        """Create form config vocabularies."""
        form_config_vocabularies = {}
        vocabularies_to_prefetch = []
        for vocabulary_type in used_vocabularies:
            vocabulary_definition = vocabulary_config.get(vocabulary_type, {})
            form_config_vocabularies[vocabulary_type] = {
                "definition": json.loads(json.dumps(vocabulary_definition, default=json_default))
            }
            if vocabulary_definition.get("dump_options"):
                vocabularies_to_prefetch.append(vocabulary_type)
                form_config_vocabularies[vocabulary_type]["all"] = []
                form_config_vocabularies[vocabulary_type]["featured"] = []
            else:
                # TODO: use vocabulary service config and prefix???
                form_config_vocabularies[vocabulary_type]["url"] = f"/api/vocabularies/{vocabulary_type}"
        return vocabularies_to_prefetch, form_config_vocabularies


def json_default(x: Any) -> Any:
    """Return json default value for json dumps."""
    if hasattr(x, "name"):
        return x.name
    if inspect.isclass(x):
        return x.__name__
    return type(x).__name__

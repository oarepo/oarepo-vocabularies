#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Component to keep rdm compatibility with skos mapping."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, cast, override

from invenio_records_resources.services.records.components import ServiceComponent

from oarepo_vocabularies.records.api import represents_export

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask_principal import Identity
    from invenio_vocabularies.records.api import Vocabulary


def _convert_url(identifier: str, fieldname: str, separator: str = "/") -> dict[str, Any]:
    """Convert a Datacite identifier in a linked-data representation to a RDM compatible prop."""
    return {fieldname: identifier.rsplit(separator, 1)[-1]}


def _convert_resource_type(identifier: str) -> dict[str, Any]:
    """Convert a Datacite resourceType identifier, adding a "type" alias for datacite_general."""
    props = _convert_url(identifier, "datacite_general")
    props["type"] = props["datacite_general"]
    return props


class RDMCompatibilitySKOSComponent(ServiceComponent):
    """Component to keep the vocabulary ID unchanged on updates."""

    _converters: ClassVar[dict[str, Callable[[str], dict[str, Any]]]] = {
        "https://schema.datacite.org/meta/kernel-4/dateType/": partial(_convert_url, fieldname="datacite"),
        "https://schema.datacite.org/meta/kernel-4/descriptionType/": partial(_convert_url, fieldname="datacite"),
        "https://schema.datacite.org/meta/kernel-4/relationType/": partial(_convert_url, fieldname="datacite"),
        "https://schema.datacite.org/meta/kernel-4/contributorType/": partial(_convert_url, fieldname="datacite"),
        "https://schema.datacite.org/meta/kernel-4/titleType/": partial(_convert_url, fieldname="datacite"),
        "https://schema.datacite.org/meta/kernel-4/resourceType/": _convert_resource_type,
        "https://guidelines.openaire.eu/en/latest/data/field_resourcetype.html#": partial(
            _convert_url, fieldname="openaire_type", separator="#"
        ),
        "info:eu-repo/semantics/": partial(_convert_url, fieldname="eurepo", separator="/"),
        "https://schema.org/": partial(_convert_url, fieldname="schema.org", separator="/"),
    }

    @override
    def create(self, identity: Identity, **kwargs: Any) -> None:
        record = cast("Vocabulary", kwargs["record"])
        self._propagate_skos_to_rdm(record)

    @override
    def update(self, identity: Identity, **kwargs: Any) -> None:
        record = cast("Vocabulary", kwargs["record"])
        self._propagate_skos_to_rdm(record)

    def _propagate_skos_to_rdm(self, record: Vocabulary) -> None:
        """Propagate known mapping from SKOS to RDM."""
        for mapping in record.get("mappings", []):
            if not represents_export(mapping):
                # invenio props are used for export only
                continue
            identifier = mapping.get("identifier")
            scheme = mapping.get("scheme")
            converter = self._converters.get(scheme)
            if converter:
                record.setdefault("props", {}).update(converter(identifier))

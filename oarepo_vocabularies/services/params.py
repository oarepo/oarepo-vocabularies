#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Param interpreter for mapping parameters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_records_resources.services.records.params import ParamInterpreter
from opensearch_dsl.query import Bool, MatchNone, Nested, Term

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_search import RecordsSearchV2


class SKOSMappingParam(ParamInterpreter):
    """Param interpreter for mapping parameters."""

    @override
    def apply(self, identity: Identity, search: RecordsSearchV2, params: dict[str, Any]) -> RecordsSearchV2:
        """Apply the parameters.

        We expect that the params contains a `skos` key with the value of:
            `exactMatch:identifier` or `exactMatch:identifier@scheme`

        We use this to filter the search results by the SKOS concept URI.
        """
        skos_params = params.get("skos")
        if not skos_params:
            return search

        def create_skos_filter(param: str) -> Any:
            if "@" in param:
                match_part, scheme = param.split("@")
            else:
                scheme = None
                match_part = param

            relation, identifier = match_part.split(":", maxsplit=1)

            musts = []
            if scheme:
                musts.append(Term(mappings__scheme=scheme))
            if relation:
                musts.append(Term(mappings__relation=relation))
            if identifier:
                musts.append(Term(mappings__identifier=identifier))

            if not musts:
                return MatchNone()

            return Nested(path="mappings", query=Bool(must=musts))

        return search.filter(Bool(should=[create_skos_filter(param) for param in skos_params], minimum_should_match=1))

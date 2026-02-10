#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""oarepo_vocabularies records API module."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, NamedTuple

from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.systemfields import ConstantField, DictField, RelationsField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.dumpers import CustomFieldsDumperExt
from invenio_records_resources.records.systemfields.pid import PIDField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation

from oarepo_vocabularies.records.systemfields.hierarchy_system_field import (
    HierarchySystemField,
)
from oarepo_vocabularies.records.systemfields.parent_system_field import (
    ParentSystemField,
)
from oarepo_vocabularies.records.systemfields.relations import (
    ParentVocabularyItemRelation,
    ParentVocabularyPIDField,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from invenio_records_resources.services.records.results import RecordItem


class Vocabulary(
    InvenioVocabulary,
):
    """Vocabulary record class with hierarchy and parent system fields."""

    pid = PIDField(
        "id",
        provider=VocabularyIdProvider,  # type: ignore[arg-type]
        context_cls=VocabularyPIDFieldContext,  # type: ignore[arg-type]
        create=False,
    )

    dumper = SearchDumper(extensions=[IndexedAtDumperExt(), CustomFieldsDumperExt("VOCABULARIES_CF")])  # type: ignore[arg-type]

    schema = ConstantField(
        "$schema",
        "local://vocabularies/vocabulary-ext-v1.0.0.json",
    )

    relations = MultiRelationsField(
        parent=ParentVocabularyItemRelation(
            "parent",
            keys=["title"],
            pid_field=ParentVocabularyPIDField(),  # type: ignore[arg-type]
        ),
        custom_fields=CustomFieldsRelation("VOCABULARIES_CF"),
    )

    parent = ParentSystemField()

    hierarchy = HierarchySystemField()
    # TODO: ICU sort field for title
    # TODO: ICU suggest field for title
    # TODO: ICU suggest field for suggest hierarchy title

    custom_fields = DictField()


class VocabularyRelation(NamedTuple):
    """A relation to a vocabulary field."""

    field_name: str
    field: RelationsField
    vocabulary_type: str


def find_vocabulary_relations(record: RecordItem) -> Iterable[VocabularyRelation]:
    """Find all vocabulary relations in a record."""
    relations_field_names = [x[0] for x in inspect.getmembers(type(record), lambda x: isinstance(x, RelationsField))]

    for relations_field_name in relations_field_names:
        # iterate all vocabularies there, check that the item exists

        relations = getattr(record, relations_field_name)

        for fld_name in relations:
            fld = getattr(relations, fld_name)
            try:
                pid_context = fld.field.pid_field
            except AttributeError:
                continue
            if isinstance(pid_context, VocabularyPIDFieldContext):
                yield VocabularyRelation(fld_name, fld, pid_context._type_id)  # noqa: SLF001 # type: ignore[attr-defined]

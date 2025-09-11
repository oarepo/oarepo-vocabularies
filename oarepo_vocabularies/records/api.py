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

from invenio_records.systemfields import ConstantField, DictField, RelationsField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.systemfields.pid import PIDField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation

from oarepo_vocabularies.proxies import current_oarepo_vocabularies
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

    from invenio_records_resources.records.api import Record


class SpecialVocabulariesAwarePIDFieldContext(VocabularyPIDFieldContext):
    """A PIDFieldContext that is aware of special vocabularies."""

    def resolve(self, pid_value: str | tuple[str, str]) -> Record | None:
        """Resolve the PID value to a record, considering special vocabularies."""
        if isinstance(pid_value, str):
            pid_type = self._type_id
            item_id = pid_value
        else:
            pid_type, item_id = pid_value

        specialized_service = current_oarepo_vocabularies.get_specialized_service(pid_type)
        if not specialized_service:
            return super().resolve(pid_value)
        return specialized_service.config.record_cls.pid.resolve(item_id)


class Vocabulary(
    InvenioVocabulary,
):
    """Vocabulary record class with hierarchy and parent system fields."""

    pid = PIDField(
        "id",
        provider=VocabularyIdProvider,
        context_cls=SpecialVocabulariesAwarePIDFieldContext,
        create=False,
    )

    schema = ConstantField(
        "$schema",
        "local://vocabularies/vocabulary-ext-v1.0.0.json",
    )

    relations = MultiRelationsField(
        parent=ParentVocabularyItemRelation(
            "parent",
            keys=["title"],
            pid_field=ParentVocabularyPIDField(),
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


def find_vocabulary_relations(record: Record) -> Iterable[VocabularyRelation]:
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
                yield VocabularyRelation(fld_name, fld, pid_context._type_id)  # noqa: SLF001

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""oarepo_vocabularies records API module."""

import inspect
from collections import namedtuple

from flask import current_app
from invenio_records.systemfields import ConstantField, DictField, RelationsField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.systemfields.pid import PIDField
from invenio_vocabularies.records.api import Vocabulary as InvenioVocabulary
from invenio_vocabularies.records.pidprovider import VocabularyIdProvider
from invenio_vocabularies.records.systemfields import VocabularyPIDFieldContext
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin

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


class SpecialVocabulariesAwarePIDFieldContext(VocabularyPIDFieldContext):
    def resolve(self, pid_value):
        if isinstance(pid_value, str):
            pid_type = self._type_id
            item_id = pid_value
        else:
            pid_type, item_id = pid_value

        specialized_service = current_oarepo_vocabularies.get_specialized_service(pid_type)
        if not specialized_service:
            return super().resolve(pid_value)
        return specialized_service.config.record_cls.pid.resolve(item_id)


class CustomFieldsMixin(MappingSystemFieldMixin):
    def __init__(self, config_key, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.config_key = config_key

    @property
    def mapping(self):
        custom_fields = current_app.config[self.config_key]
        return {cf.name: cf.mapping for cf in custom_fields}

    @property
    def mapping_settings(self):
        return {}

    def search_dump(self, data, record):
        custom_fields = current_app.config.get(self.config_key, {})

        for cf in custom_fields:
            cf.dump(data, cf_key=self.key)
        return data

    def search_load(self, data, record_cls):
        custom_fields = current_app.config.get(self.config_key, {})

        for cf in custom_fields:
            cf.load(data, cf_key=self.key)
        return data


class Vocabulary(
    InvenioVocabulary,
):
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
    # sort = ICUSortField(source_field="title")
    # suggest = ICUSuggestField(source_field="title")
    # suggest_hierarchy = ICUSuggestField(source_field="hierarchy.title")

    custom_fields = DictField()


VocabularyRelation = namedtuple("VocabularyRelation", "field_name, field, vocabulary_type")


def find_vocabulary_relations(record):
    relations_field_names = [x[0] for x in inspect.getmembers(type(record), lambda x: isinstance(x, RelationsField))]

    for relations_field_name in relations_field_names:
        # iterate all vocabularies there, check that the item exists

        relations = getattr(record, relations_field_name)

        for fld_name in relations:
            fld = getattr(relations, fld_name)
            try:
                pid_context = fld.field.pid_field
            except:
                continue
            if isinstance(pid_context, VocabularyPIDFieldContext):
                yield VocabularyRelation(fld_name, fld, pid_context._type_id)

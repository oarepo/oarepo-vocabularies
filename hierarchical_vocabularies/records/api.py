# -*- coding: utf-8 -*-
from invenio_vocabularies.records.api import Vocabulary
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.systemfields import IndexField


class HVocabulary(Vocabulary):
    """Hierarchical vocabulary record."""

    # System fields
    schema = ConstantField(
        "$schema",
        "local://hvocabularies/hvocabulary-v1.0.0.json",
    )

    index = IndexField("hvocabularies-hvocabulary-v1.0.0", search_alias="hvocabularies")

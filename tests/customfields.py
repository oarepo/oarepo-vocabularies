#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import marshmallow as ma
from invenio_records_resources.services.custom_fields import BaseCF
from invenio_vocabularies.services.schema import i18n_strings


class RelatedURICF(BaseCF):
    """Custom field for related URIs."""

    @property
    def mapping(self):
        """Return the mapping."""
        return {"type": "object", "dynamic": True}

    @property
    def field(self):
        """Marshmallow field for custom fields."""
        return ma.fields.Dict(keys=ma.fields.Str(), values=ma.fields.Str())


class NonPreferredLabelsCF(BaseCF):
    """Non preferred labels custom field."""

    @property
    def mapping(self):
        """Return the mapping."""
        return {"type": "object", "dynamic": True}

    @property
    def field(self):
        """Marshmallow field for custom fields."""
        return ma.fields.List(i18n_strings)


class HintCF(BaseCF):
    """Custom field for hint."""

    @property
    def mapping(self):
        """Return the mapping."""
        return {"type": "object", "dynamic": True}

    @property
    def field(self):
        """Marshmallow field for custom fields."""
        return i18n_strings

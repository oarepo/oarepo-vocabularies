#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from flask_resources import BaseObjectSchema
from marshmallow import post_dump

from oarepo_vocabularies.services.ui_schema import VocabularyI18nStrUIField


class VocabularyTypeUISchema(BaseObjectSchema):
    name = VocabularyI18nStrUIField()

    description = VocabularyI18nStrUIField()

    @post_dump(pass_original=True)
    def keep_unknowns(self, output, orig, **kwargs):
        for key in orig:
            if key not in output:
                output[key] = orig[key]
        return output

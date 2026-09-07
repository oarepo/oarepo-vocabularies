#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-vocabularies (see https://github.com/oarepo/oarepo-vocabularies).
#
# oarepo-vocabularies is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from invenio_vocabularies.jobs import (
    ProcessRORAffiliationsJob,
    ProcessRORFundersJob,
)

from oarepo_vocabularies.ext import enable_datastream_updates


def test_ror_jobs_update_existing_entries():
    enable_datastream_updates()

    affiliations = ProcessRORAffiliationsJob.build_task_arguments(None)
    funders = ProcessRORFundersJob.build_task_arguments(None)

    affiliations_writer = affiliations["config"]["writers"][0]["args"]["writer"]
    funders_writer = funders["config"]["writers"][0]["args"]["writer"]

    assert affiliations_writer["args"]["update"] is True
    assert funders_writer["args"]["update"] is True

# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for the ORCID public data file import job."""

from __future__ import annotations

import pytest
from marshmallow import ValidationError

from oarepo_vocabularies.orcid.jobs import (
    JOB_ARG_SCHEMA_NAME,
    ImportORCIDDumpArgsSchema,
    ImportORCIDDumpJob,
)
from oarepo_vocabularies.orcid.tasks import DEFAULT_BATCH_SIZE, import_orcid_dump


def test_job_definition():
    assert ImportORCIDDumpJob.id == "import_orcid_dump"
    assert ImportORCIDDumpJob.task is import_orcid_dump
    assert ImportORCIDDumpJob.arguments_schema is ImportORCIDDumpArgsSchema
    assert ImportORCIDDumpJob.title
    assert ImportORCIDDumpJob.description


def test_job_task_is_a_celery_task():
    assert hasattr(ImportORCIDDumpJob.task, "delay")


def test_build_task_arguments_passes_everything_through():
    arguments = ImportORCIDDumpJob.build_task_arguments(
        None,
        year=2026,
        url="https://example.org/summaries.tar.gz",
        limit=10,
        batch_size=1000,
        update_existing=True,
    )

    assert arguments == {
        "year": 2026,
        "url": "https://example.org/summaries.tar.gz",
        "limit": 10,
        "batch_size": 1000,
        "update": True,
    }


def test_build_task_arguments_fills_in_defaults():
    arguments = ImportORCIDDumpJob.build_task_arguments(None)

    assert arguments["batch_size"] == DEFAULT_BATCH_SIZE
    assert arguments["update"] is False
    assert arguments["year"] is None
    assert arguments["limit"] is None


def test_arguments_schema_loads_empty_payload():
    loaded = ImportORCIDDumpArgsSchema().load({})

    assert loaded["batch_size"] == DEFAULT_BATCH_SIZE
    assert loaded["update_existing"] is False
    assert loaded["year"] is None
    assert loaded["url"] is None
    assert loaded["limit"] is None


def test_update_flag_is_not_confused_with_dict_update():
    """Marshmallow falls back to getattr() for missing dict keys, and dict.update is truthy."""
    schema = ImportORCIDDumpArgsSchema()

    assert "update_existing" not in schema.dump({})
    assert schema.load({})["update_existing"] is False


def test_schema_name_matches_the_class_name():
    """invenio_jobs dispatches on this value; a mismatch rejects every field as unknown."""
    assert ImportORCIDDumpArgsSchema.__name__ == JOB_ARG_SCHEMA_NAME
    assert ImportORCIDDumpArgsSchema().dump({})["job_arg_schema"] == ImportORCIDDumpArgsSchema.__name__


def test_dispatcher_resolves_this_schema():
    """Mimic JobArgumentsSchema: it looks the schema up by the submitted type field."""
    type_schemas = {ImportORCIDDumpArgsSchema.__name__: ImportORCIDDumpArgsSchema}

    # what the admin form sends back, built from the defaults jsonify_schema exposes
    submitted = ImportORCIDDumpArgsSchema().dump({"limit": 10})

    assert type_schemas[submitted["job_arg_schema"]]().load(submitted)["limit"] == 10


def test_schema_does_not_expose_since():
    """A yearly snapshot has no incremental window; the field would be a dead input."""
    assert "since" not in ImportORCIDDumpArgsSchema().fields


def test_arguments_schema_rejects_a_non_numeric_year():
    with pytest.raises(ValidationError):
        ImportORCIDDumpArgsSchema().load({"year": "not-a-year"})

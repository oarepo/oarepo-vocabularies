# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Invenio job importing the ORCID public data file."""

from __future__ import annotations

from typing import Any

from invenio_i18n import gettext as _
from invenio_jobs.jobs import JobType
from marshmallow import Schema, fields

from oarepo_vocabularies.orcid.tasks import DEFAULT_BATCH_SIZE, import_orcid_dump

JOB_ARG_SCHEMA_NAME = "ImportORCIDDumpArgsSchema"
"""Name under which the job arguments schema is registered.

``invenio_jobs`` dispatches the run arguments with a marshmallow ``OneOfSchema`` whose
type field is ``job_arg_schema``; the value has to match the class name of the schema,
otherwise the arguments are validated against ``PredefinedArgsSchema`` and every field
below is rejected as unknown. Keep it in sync with the class name (there is a test).
"""


class ImportORCIDDumpArgsSchema(Schema):
    """Arguments of the ORCID public data file import.

    Deliberately not a ``PredefinedArgsSchema``: that schema only offers ``since``, which
    has no meaning for a yearly snapshot, and it would be rendered in the job form.
    """

    job_arg_schema = fields.String(
        load_default=JOB_ARG_SCHEMA_NAME,
        dump_default=JOB_ARG_SCHEMA_NAME,
        metadata={"type": "hidden"},
    )

    year = fields.Integer(
        allow_none=True,
        load_default=None,
        metadata={
            "title": _("Release year"),
            "description": _("Release year of the public data file. Leave empty to use the configured year."),
        },
    )
    url = fields.Str(
        allow_none=True,
        load_default=None,
        metadata={
            "title": _("Archive url"),
            "description": _("Archive url. When set, the Figshare discovery is skipped."),
        },
    )
    limit = fields.Integer(
        allow_none=True,
        load_default=None,
        metadata={
            "title": _("Record limit"),
            "description": _("Stop after this many records. Useful for a smoke test."),
        },
    )
    batch_size = fields.Integer(
        allow_none=True,
        load_default=DEFAULT_BATCH_SIZE,
        metadata={
            "title": _("Batch size"),
            "description": _("Number of records per celery message."),
        },
    )
    # named update_existing rather than update: marshmallow falls back to getattr() for
    # keys missing from a dict, and `dict.update` is a truthy bound method
    update_existing = fields.Boolean(
        allow_none=True,
        load_default=False,
        metadata={
            "title": _("Update existing records"),
            "description": _("Update records that already exist instead of skipping them."),
        },
    )


class ImportORCIDDumpJob(JobType):
    """Import the ORCID public data file into the names vocabulary."""

    id = "import_orcid_dump"
    title = _("Import Annual ORCID Public Data File")
    description = _(
        "Stream the annual ORCID public data file from Figshare and import the name "
        "records in bulk. The file is read from the network, never stored on the disk."
    )
    task = import_orcid_dump
    arguments_schema = ImportORCIDDumpArgsSchema

    @classmethod
    def build_task_arguments(
        cls,
        job_obj: Any,  # noqa: ARG003
        since: Any = None,  # noqa: ARG003
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Map the job arguments onto the celery task keyword arguments."""
        return {
            "year": kwargs.get("year"),
            "url": kwargs.get("url"),
            "limit": kwargs.get("limit"),
            "batch_size": kwargs.get("batch_size") or DEFAULT_BATCH_SIZE,
            "update": bool(kwargs.get("update_existing")),
        }


__all__ = ["JOB_ARG_SCHEMA_NAME", "ImportORCIDDumpArgsSchema", "ImportORCIDDumpJob"]

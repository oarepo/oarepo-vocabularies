# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Celery task importing the ORCID public data file."""

from __future__ import annotations

from itertools import islice
from typing import TYPE_CHECKING, Any

from celery import shared_task
from flask import current_app
from invenio_jobs.errors import TaskExecutionPartialError
from invenio_vocabularies.datastreams.factories import DataStreamFactory

from oarepo_vocabularies.orcid.figshare import resolve_dump
from oarepo_vocabularies.orcid.urls import sanitize_url

if TYPE_CHECKING:
    from collections.abc import Iterator

    from invenio_vocabularies.datastreams.datastreams import StreamEntry

DEFAULT_BATCH_SIZE = 5000
"""Number of records per celery message."""

LOG_EVERY = 100_000
"""Number of processed entries between two progress log lines."""

TRANSFORMERS_CONFIG = [{"type": "orcid"}]
"""Reuses the stock ORCID XML to name record transformer."""


def readers_config(archive_url: str) -> list[dict[str, Any]]:
    """Return the readers streaming the archive, without staging it on the disk."""
    return [
        {"type": "orcid-http-stream", "args": {"url": archive_url}},
        # not the stock "tar" reader: it keeps every TarInfo in memory (see the class)
        {"type": "orcid-tar", "args": {"regex": r"\.xml$"}},
        {"type": "xml", "args": {"root_element": "record"}},
    ]


def writers_config(update: bool = False) -> list[dict[str, Any]]:
    """Return the writers fanning the batch writes out to celery workers."""
    return [
        {
            # one celery message per batch; the worker rebuilds the inner writer from
            # this config dict (see invenio_vocabularies.datastreams.tasks)
            "type": "async",
            "args": {"writer": {"type": "names-bulk", "args": {"update": update}}},
        }
    ]


@shared_task(ignore_result=True)
def import_orcid_dump(
    year: int | None = None,
    url: str | None = None,
    limit: int | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    update: bool = False,
) -> None:
    """Stream the ORCID public data file and dispatch batched writes to workers.

    Only this task reads the archive; the writes are handed over to celery by the
    ``async`` writer, one message per ``batch_size`` records. Memory is bounded by a
    single batch and nothing is written to the disk.
    """
    if url:
        archive_url = sanitize_url(url)
        current_app.logger.info("Importing ORCID public data file from %s", archive_url)
    else:
        dump = resolve_dump(year=year)
        archive_url = dump.download_url
        current_app.logger.info(
            "Importing ORCID public data file %s (%s, %.1f GB, md5 %s, article %s)",
            dump.year,
            dump.name,
            dump.size / 1e9,
            dump.md5,
            dump.article_id,
        )

    datastream = DataStreamFactory.create(
        readers_config=readers_config(archive_url),
        transformers_config=TRANSFORMERS_CONFIG,
        writers_config=writers_config(update=update),
        batch_size=batch_size,
        write_many=True,
        run_subtasks=True,
    )

    results: Iterator[StreamEntry] = datastream.process()
    if limit:
        results = islice(results, limit)

    total = 0
    errors = 0
    for result in results:
        total += 1
        if result.errors:
            errors += 1
        if total % LOG_EVERY == 0:
            current_app.logger.info(
                "ORCID import progress: %s entries dispatched, %s transform errors",
                total,
                errors,
            )

    current_app.logger.info("ORCID public data file dispatched: %s entries, %s transform errors", total, errors)
    if errors:
        raise TaskExecutionPartialError(
            message=f"{errors} ORCID entries failed transformation",
            errored_entries_count=errors,
        )


__all__ = ["import_orcid_dump"]

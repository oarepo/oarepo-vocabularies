# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Import of the annual ORCID Public Data File published on Figshare.

The package provides the pieces needed to load the ORCID registry snapshot into the
``names`` vocabulary without going through the (very slow) per-record service call:

- :mod:`oarepo_vocabularies.orcid.figshare` discovers the newest public data file,
- :mod:`oarepo_vocabularies.orcid.readers` streams the archive without touching the disk,
- :mod:`oarepo_vocabularies.orcid.writers` writes batches straight to the database and index,
- :mod:`oarepo_vocabularies.orcid.jobs` exposes the whole thing as an Invenio job.
"""

from __future__ import annotations

from oarepo_vocabularies.orcid.figshare import OrcidDump, OrcidDumpError, resolve_dump
from oarepo_vocabularies.orcid.readers import HttpStreamReader

__all__ = ["HttpStreamReader", "OrcidDump", "OrcidDumpError", "resolve_dump"]

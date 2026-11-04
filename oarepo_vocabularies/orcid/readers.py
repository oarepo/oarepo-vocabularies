# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Datastream readers for the ORCID public data file."""

# datastream components implement the framework base-class signatures, which pass
# arguments they do not necessarily use
# ruff: noqa: ARG002

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.request import urlopen

from invenio_vocabularies.datastreams.readers import BaseReader, TarReader

from oarepo_vocabularies.orcid.urls import sanitize_url

if TYPE_CHECKING:
    import re
    from collections.abc import Generator, Iterator


class HttpStreamReader(BaseReader):
    r"""Yield a single HTTP response body as a stream.

    The reader produces exactly one item, so it has to be the first reader of a
    pipeline. The following reader (typically ``tar``) receives the response object
    as its ``item`` argument; :class:`invenio_vocabularies.datastreams.readers.TarReader`
    then opens it in streaming mode (``r|gz``), which neither buffers the archive nor
    writes it to the disk.

    Usage::

        (
            {
                "type": "orcid-http-stream",
                "args": {
                    "url": "https://.../summaries.tar.gz"
                },
            },
        )
        (
            {
                "type": "orcid-tar",
                "args": {"regex": r"\\.xml$"},
            },
        )
        (
            {
                "type": "xml",
                "args": {
                    "root_element": "record"
                },
            },
        )
    """

    def __init__(self, url: str, *args: Any, timeout: int = 300, **kwargs: Any) -> None:
        """Initialize the reader.

        :param url: url of the archive (redirects are followed).
        :param timeout: socket timeout in seconds.
        """
        super().__init__(*args, **kwargs)
        self._url = url
        self._timeout = timeout

    def _iter(self, fp: Any, *args: Any, **kwargs: Any) -> Iterator[Any]:
        """Not used: this reader produces a single item and is then exhausted."""
        yield from ()

    def read(self, item: Any = None, *args: Any, **kwargs: Any) -> Generator[Any]:
        """Open the url and yield the response body as a single item."""
        url = sanitize_url(self._url)
        with urlopen(url, timeout=self._timeout) as response:  # noqa: S310
            yield response


class StreamingTarReader(TarReader):
    """Tar reader that does not keep the headers of the members it has already read.

    :class:`tarfile.TarFile` appends every header it reads to ``TarFile.members``, in
    stream mode (``r|gz``) as well. The ORCID summaries archive contains tens of millions
    of files, so the stock ``tar`` reader grows by roughly 0.5 kB per record until the
    worker runs out of memory. In stream mode a member can not be revisited anyway, so
    the list is cleared after every member.
    """

    _regex: re.Pattern[str] | None
    """Set by :class:`TarReader` from the ``regex`` argument (not declared in its stubs)."""

    def _iter(self, fp: Any, *args: Any, **kwargs: Any) -> Iterator[Any]:
        """Iterate through the files in the archive, discarding consumed headers."""
        for member in fp:
            match = not self._regex or self._regex.search(member.name)
            if member.isfile() and match:
                yield fp.extractfile(member)
            fp.members.clear()


VOCABULARIES_DATASTREAM_READERS = {
    "orcid-http-stream": HttpStreamReader,
    "orcid-tar": StreamingTarReader,
}
"""Readers contributed by :mod:`oarepo_vocabularies.orcid`."""

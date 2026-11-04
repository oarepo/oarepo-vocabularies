# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for streaming the ORCID archive from an http response."""

from __future__ import annotations

import io
import tarfile

import pytest
from flask import Flask
from invenio_vocabularies.datastreams.datastreams import DataStream
from invenio_vocabularies.datastreams.readers import XMLReader

from oarepo_vocabularies.orcid import readers as readers_module
from oarepo_vocabularies.orcid.readers import HttpStreamReader, StreamingTarReader


@pytest.fixture
def app_ctx():
    """Provide a bare flask application context: the datastream only needs a logger."""
    app = Flask(__name__)
    with app.app_context():
        yield app


ORCID_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<record xmlns="http://www.orcid.org/ns/orcid">
  <orcid-identifier><path>0000-0002-1825-0097</path></orcid-identifier>
  <person>
    <name><given-names>Josiah</given-names><family-name>Carberry</family-name></name>
  </person>
</record>
"""


class _StrictStream:
    """Non-seekable body that returns fewer bytes than requested (like a socket)."""

    def __init__(self, data: bytes, max_chunk: int = 7) -> None:
        self._data = data
        self._pos = 0
        self._max_chunk = max_chunk

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = len(self._data) - self._pos
        chunk = self._data[self._pos : self._pos + min(size, self._max_chunk)]
        self._pos += len(chunk)
        return chunk

    def seekable(self) -> bool:
        return False

    def seek(self, *args):
        raise io.UnsupportedOperation("seek")

    def tell(self):
        raise io.UnsupportedOperation("tell")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def _tar_gz(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, payload in entries.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


def test_streams_a_tar_gz_from_a_non_seekable_response(app_ctx, monkeypatch):
    blob = _tar_gz({"097/0000-0002-1825-0097.xml": ORCID_XML})
    monkeypatch.setattr(readers_module, "urlopen", lambda url, timeout=None: _StrictStream(blob))

    datastream = DataStream(
        readers=[
            HttpStreamReader("https://example.org/summaries.tar.gz"),
            StreamingTarReader(regex=r"\.xml$"),
            XMLReader(root_element="record"),
        ],
        writers=[],
        transformers=[],
        batch_size=10,
    )
    records = [stream_entry.entry for stream_entry in datastream.read()]

    assert len(records) == 1
    assert records[0]["orcid-identifier"]["path"] == "0000-0002-1825-0097"
    assert records[0]["person"]["name"]["family-name"] == "Carberry"


def test_yields_exactly_one_item(app_ctx, monkeypatch):
    blob = _tar_gz({"a.xml": ORCID_XML})
    monkeypatch.setattr(readers_module, "urlopen", lambda url, timeout=None: _StrictStream(blob))

    items = list(HttpStreamReader("https://example.org/summaries.tar.gz").read())

    assert len(items) == 1


def test_tar_reader_does_not_accumulate_members():
    blob = _tar_gz({f"{i:03d}/0000-0002-1825-{i:04d}.xml": ORCID_XML for i in range(50)} | {"README.txt": b"x"})

    with tarfile.open(fileobj=_StrictStream(blob, max_chunk=4096), mode="r|gz") as archive:
        reader = StreamingTarReader(regex=r"\.xml$")
        count = 0
        for fp in reader.read(archive):
            assert fp.read() == ORCID_XML
            # tarfile appends every header to `members`; the reader must drop them
            assert len(archive.members) <= 1
            count += 1
        assert archive.members == []

    assert count == 50

# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Tests for the registration of the ORCID datastream components."""

from __future__ import annotations

from flask import Flask

from oarepo_vocabularies.ext import OARepoVocabularies
from oarepo_vocabularies.orcid.readers import HttpStreamReader, StreamingTarReader
from oarepo_vocabularies.orcid.writers import NamesBulkWriter

EXISTING_READER = object()
EXISTING_WRITER = object()


def test_extension_merges_the_datastream_registries():
    app = Flask(__name__)
    app.config["VOCABULARIES_DATASTREAM_READERS"] = {"tar": EXISTING_READER}
    app.config["VOCABULARIES_DATASTREAM_WRITERS"] = {"names-service": EXISTING_WRITER}

    OARepoVocabularies().init_datastreams(app)

    # the stock readers/writers must survive: replacing the dicts would break ROR imports
    assert app.config["VOCABULARIES_DATASTREAM_READERS"]["tar"] is EXISTING_READER
    assert app.config["VOCABULARIES_DATASTREAM_WRITERS"]["names-service"] is EXISTING_WRITER
    assert app.config["VOCABULARIES_DATASTREAM_READERS"]["orcid-http-stream"] is HttpStreamReader
    assert app.config["VOCABULARIES_DATASTREAM_READERS"]["orcid-tar"] is StreamingTarReader
    assert app.config["VOCABULARIES_DATASTREAM_WRITERS"]["names-bulk"] is NamesBulkWriter


def test_extension_registers_into_an_empty_config():
    app = Flask(__name__)

    OARepoVocabularies().init_datastreams(app)

    assert set(app.config["VOCABULARIES_DATASTREAM_READERS"]) == {"orcid-http-stream", "orcid-tar"}
    assert set(app.config["VOCABULARIES_DATASTREAM_WRITERS"]) == {"names-bulk"}

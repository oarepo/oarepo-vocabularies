from pathlib import Path

from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import load_fixtures
from oarepo_runtime.datastreams.types import StatsKeepingDataStreamCallback


def test_complex_import_export(app, db, cache, vocab_cf):
    callback = StatsKeepingDataStreamCallback()
    load_fixtures(
        Path(__file__).parent / "complex-data",
        callback=callback,
    )

    assert callback.ok_entries_count == 2737
    assert callback.failed_entries_count == 0
    assert callback.filtered_entries_count == 0
    Vocabulary.index.refresh()

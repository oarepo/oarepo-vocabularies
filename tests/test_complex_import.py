from pathlib import Path

import pytest
from invenio_vocabularies.records.api import Vocabulary


@pytest.mark.skip
def test_complex_import_export(app, db, cache, vocab_cf):
    class ErrCallback(FixturesCallback):
        def batch_finished(self, batch: StreamBatch):
            if batch.failed_entries:
                print(batch.failed_entries)
            super().batch_finished(batch)

    callback = ErrCallback()
    load_fixtures(
        Path(__file__).parent / "complex-data",
        callback=callback,
    )

    assert callback.ok_entries_count == 2737
    assert callback.failed_entries_count == 0
    assert callback.filtered_entries_count == 0
    Vocabulary.index.refresh()

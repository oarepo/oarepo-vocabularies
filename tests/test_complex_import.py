from pathlib import Path
from invenio_access.permissions import system_identity

from oarepo_runtime.datastreams.fixtures import load_fixtures

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.proxies import current_service


def test_complex_import_export(app, db, cache, vocab_cf):
    result = load_fixtures(
        Path(__file__).parent / "complex-data",
    )
    assert result.ok_count == 2737
    assert result.failed_count == 0
    assert result.skipped_count == 0
    assert len(result.results) == 11
    Vocabulary.index.refresh()

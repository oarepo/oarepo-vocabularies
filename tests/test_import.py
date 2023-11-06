import tempfile
from pathlib import Path

import yaml
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import dump_fixtures, load_fixtures
from oarepo_runtime.datastreams.types import StatsKeepingDataStreamCallback


def read_yaml(fp):
    with open(fp) as f:
        ret = list(yaml.safe_load_all(f))
        if len(ret) == 1:
            return ret[0]
        return ret


def test_import_export_hierarchy_data(app, db, cache, vocab_cf):
    callback = StatsKeepingDataStreamCallback()
    load_fixtures(Path(__file__).parent / "data", callback=callback)
    assert callback.ok_entries_count == 2
    assert callback.failed_entries_count == 0
    assert callback.filtered_entries_count == 0

    Vocabulary.index.refresh()

    assert current_service.read(system_identity, ("languages", "en")).data["id"] == "en"
    assert current_service.read(system_identity, ("languages", "en.US")).data[
        "hierarchy"
    ]["ancestors"] == ["en"]

    with tempfile.TemporaryDirectory() as d:
        callback = StatsKeepingDataStreamCallback()
        dump_fixtures(d, include=["vocabulary-languages"], callback=callback)
        assert callback.ok_entries_count == 2
        assert callback.failed_entries_count == 0
        assert callback.filtered_entries_count == 0
        d = Path(d)
        assert read_yaml(d / "catalogue.yaml") == {
            "vocabulary-languages": [
                {"pid_type": "lng", "vocabulary": "languages", "writer": "vocabulary"},
                {"source": "vocabulary-languages.yaml"},
            ]
        }
        assert set(
            x["title"]["en"] for x in read_yaml(d / "vocabulary-languages.yaml")
        ) == {"English", "English (US)"}

from pathlib import Path
from invenio_access.permissions import system_identity

from oarepo_runtime.datastreams.fixtures import load_fixtures, dump_fixtures

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.proxies import current_service
import tempfile
import yaml


def read_yaml(fp):
    with open(fp) as f:
        ret = list(yaml.safe_load_all(f))
        if len(ret) == 1:
            return ret[0]
        return ret


def test_import_export_hierarchy_data(app, db, cache, vocab_cf):
    result = load_fixtures(Path(__file__).parent / "data")
    assert result.ok_count == 2
    assert result.failed_count == 0
    assert result.skipped_count == 0

    Vocabulary.index.refresh()

    assert current_service.read(system_identity, ("languages", "en")).data["id"] == "en"
    assert current_service.read(system_identity, ("languages", "en.US")).data[
        "hierarchy"
    ]["ancestors"] == ["en"]

    with tempfile.TemporaryDirectory() as d:
        result = dump_fixtures(d, include=["vocabulary-languages"])
        assert result.ok_count == 2
        assert result.failed_count == 0
        assert result.skipped_count == 0
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

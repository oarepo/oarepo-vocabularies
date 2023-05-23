from invenio_records_resources.services import Link
from invenio_vocabularies.services import VocabulariesServiceConfig

from oarepo_vocabularies.records.api import Vocabulary
from oarepo_vocabularies.services.components.hierarchy import HierarchyComponent
from oarepo_vocabularies.services.schema import VocabularySchema
from oarepo_vocabularies.services.search import VocabularySearchOptions


class VocabulariesConfig(VocabulariesServiceConfig):
    record_cls = Vocabulary
    schema = VocabularySchema
    search = VocabularySearchOptions
    components = [*VocabulariesServiceConfig.components, HierarchyComponent]
    url_prefix = "/vocabularies/"
    links_item = {
        **VocabulariesServiceConfig.links_item,
        "vocabulary": Link(
            "{+api}/vocabularies/{type}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                }
            ),
        ),
        "parent": Link(
            "{+api}/vocabularies/{type}/{parent}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "parent": record.get("hierarchy", {}).get("parent"),
                }
            ),
            when=lambda obj, ctx: bool(obj.get("hierarchy", {}).get("parent")),
        ),
        "children": Link(
            "{+api}/vocabularies/{type}?h-parent={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
        "descendants": Link(
            "{+api}/vocabularies/{type}?h-ancestor={id}",
            vars=lambda record, vars: vars.update(
                {
                    "type": record.type.id,
                    "id": record.pid.pid_value,
                }
            ),
        ),
    }

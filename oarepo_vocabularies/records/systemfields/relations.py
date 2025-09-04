from invenio_records.systemfields.relations.results import RelationResult
from invenio_records_resources.records.systemfields.relations import PIDRelation
from invenio_vocabularies.records.api import Vocabulary


class ParentVocabularyItemRelationResult(RelationResult):
    def _lookup_id(self):
        id_ = super()._lookup_id()
        vocabulary_type = self.record["type"]["id"]

        return (vocabulary_type, id_)


class ParentVocabularyItemRelation(PIDRelation):
    result_cls = ParentVocabularyItemRelationResult


class ParentVocabularyPIDField:
    def resolve(self, id_: tuple[str, str]):
        vocabulary_type, item_id = id_
        return Vocabulary.pid.with_type_ctx(vocabulary_type).resolve(item_id)

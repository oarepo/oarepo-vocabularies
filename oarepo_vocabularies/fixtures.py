from invenio_db import db
from invenio_vocabularies.records.api import VocabularyType
from oarepo_runtime.datastreams.readers.service import ServiceReader
from oarepo_runtime.datastreams.writers.service import ServiceWriter, StreamEntry


def vocabularies_generator(service_id, **kwargs):
    vocabularies = VocabularyType.query.all()
    for vocab_type in vocabularies:
        loader = [
            {
                "writer": "vocabulary",
                "vocabulary": vocab_type.id,
                "pid_type": vocab_type.pid_type,
            },
            {"source": f"vocabulary-{vocab_type.id}.yaml"},
        ]

        dumper = [
            {"reader": "vocabulary", "vocabulary": vocab_type.id},
            {"writer": "yaml", "target": f"vocabulary-{vocab_type.id}.yaml"},
        ]
        yield f"vocabulary-{vocab_type.id}", loader, dumper


class VocabularyReader(ServiceReader):
    def __init__(self, *, vocabulary=None, identity=None, **kwargs):
        super().__init__(service="vocabularies", identity=identity, **kwargs)
        self.vocabulary = vocabulary

    def __iter__(self):
        # invenio-vocabularies has no filter on type id, so need to scan everything
        # hopefully this is not a too frequent op
        for rec in self._service.scan(self._identity):
            if rec["type"] == self.vocabulary:
                rec = dict(rec)
                rec.pop("type")
                yield StreamEntry(rec)


class VocabularyWriter(ServiceWriter):
    def __init__(
        self,
        *,
        vocabulary=None,
        pid_type=None,
        identity=None,
        update=False,
        **kwargs,
    ):
        super().__init__(
            service="vocabularies", identity=identity, update=update, **kwargs
        )
        self.vocabulary = vocabulary
        self.pid_type = pid_type
        vt = VocabularyType.query.filter_by(id=self.vocabulary).one_or_none()
        if not vt:
            vt = VocabularyType(id=self.vocabulary, pid_type=self.pid_type)
            db.session.add(vt)
            db.session.commit()

    def write(self, stream_entry: StreamEntry, *args, **kwargs):
        entry = stream_entry.entry
        entry["type"] = self.vocabulary
        return super().write(stream_entry, *args, **kwargs)

    def _entry_id(self, entry):
        return (self.vocabulary, super()._entry_id(entry))

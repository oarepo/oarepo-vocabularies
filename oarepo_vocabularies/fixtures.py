import functools
from typing import Union

from invenio_db import db
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.models import AffiliationsMetadata
from invenio_vocabularies.contrib.awards.models import AwardsMetadata
from invenio_vocabularies.contrib.funders.models import FundersMetadata
from invenio_vocabularies.contrib.names.models import NamesMetadata
from invenio_vocabularies.records.api import VocabularyType
from oarepo_runtime.datastreams import StreamBatch
from oarepo_runtime.datastreams.readers.service import ServiceReader
from oarepo_runtime.datastreams.types import StreamBatch
from oarepo_runtime.datastreams.writers import BaseWriter
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

    def write(self, stream_batch: StreamBatch, *args, **kwargs):
        for stream_entry in stream_batch.entries:
            entry = stream_entry.entry
            entry["type"] = self.vocabulary
        return super().write(stream_batch, *args, **kwargs)

    def _get_stream_entry_id(self, entry):
        _id = entry.entry.get("id", None)
        if _id:
            return (self.vocabulary, _id)
        return None


class AwardsWriter(BaseWriter):
    """Optimized writer for awards."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def write(self, batch: StreamBatch) -> Union[StreamBatch, None]:
        """Writes the input entry to the target output.
        :returns: nothing
                  Raises WriterException in case of errors.
        """
        awards_service = current_service_registry.get("awards")

        awards = []
        for entry in batch.ok_entries:
            payload = entry.entry
            stored = AwardsMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                awards.append(stored)
                continue

            pid = payload.pop("id")
            if "funder" in payload:
                funder_id = payload["funder"].get("id")
                payload["funder"]["name"] = self.lookup_funder_name(funder_id)
            award = AwardsMetadata(pid=pid, json=payload)
            db.session.add(award)
            awards.append(award)
            entry.id = award.pid

        db.session.commit()
        awards_service.indexer.bulk_index([award.id for award in awards])

        return batch

    def finish(self):
        pass

    @functools.lru_cache(maxsize=1024)
    def lookup_funder_name(self, funder_id):
        """Lookup funder name by id."""
        funder = FundersMetadata.query.filter_by(pid=funder_id).one()
        return funder.json["name"]


class NamesWriter(BaseWriter):
    """Optimized writer for names."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def write(self, batch: StreamBatch) -> Union[StreamBatch, None]:
        """Writes the input entry to the target output.
        :returns: nothing
                  Raises WriterException in case of errors.
        """
        names_service = current_service_registry.get("names")

        names = []
        for entry in batch.ok_entries:
            payload = entry.entry
            if "affiliations" in payload:
                raise Exception("Affiliations are not supported in this writer")
            stored = NamesMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                names.append(stored)
                continue

            pid = payload.pop("id")
            name = NamesMetadata(pid=pid, json=payload)
            db.session.add(name)
            names.append(name)
            entry.id = name.pid

        db.session.commit()
        names_service.indexer.bulk_index([name.id for name in names])

        return batch

    def finish(self):
        pass


class AffiliationsWriter(BaseWriter):
    """Optimized writer for awards."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def write(self, batch: StreamBatch) -> Union[StreamBatch, None]:
        """Writes the input entry to the target output.
        :returns: nothing
                  Raises WriterException in case of errors.
        """
        affiliations_service = current_service_registry.get("affiliations")

        affiliations = []
        for entry in batch.ok_entries:
            payload = entry.entry
            stored = AffiliationsMetadata.query.filter_by(pid=payload["id"]).first()
            if stored:
                entry.id = payload["id"]
                affiliations.append(stored)
                continue

            pid = payload.pop("id")
            affiliation = AffiliationsMetadata(pid=pid, json=payload)
            db.session.add(affiliation)
            affiliations.append(affiliation)
            entry.id = affiliation.pid

        db.session.commit()
        affiliations_service.indexer.bulk_index(
            [affiliation.id for affiliation in affiliations]
        )

        return batch

    def finish(self):
        pass

from invenio_db import db
from invenio_records.models import RecordMetadataBase


class OARepoVocabularyMetadataBase(db.Model, RecordMetadataBase):
    __abstract__ = True

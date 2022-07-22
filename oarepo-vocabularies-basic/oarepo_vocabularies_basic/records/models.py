from invenio_db import db
from invenio_records.models import RecordMetadataBase
from oarepo_vocabularies.records.models import OARepoVocabularyMetadataBase


class OARepoVocabulariesBasicMetadata(
    OARepoVocabularyMetadataBase, db.Model, RecordMetadataBase
):
    """Model for OARepoVocabularyBasic metadata."""

    __tablename__ = "oarepovocabulariesbasic_metadata"

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}

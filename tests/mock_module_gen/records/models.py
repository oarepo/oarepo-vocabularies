from invenio_db import db
from invenio_records.models import RecordMetadataBase


class MockModuleGenMetadata(db.Model, RecordMetadataBase):
    """Model for MockModuleGenRecord metadata."""

    __tablename__ = "mockmodulegen_metadata"

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}

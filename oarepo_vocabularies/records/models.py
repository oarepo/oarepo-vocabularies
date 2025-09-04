"""Vocabulary models."""

from invenio_db import db
from sqlalchemy_utils.types import UUIDType


class VocabularyHierarchy(db.Model):
    """Vocabulary hierarchy model."""

    __tablename__ = "vocabularies_hierarchy"

    id = db.Column(
        UUIDType, db.ForeignKey("vocabularies_metadata.id"), primary_key=True
    )
    parent_id = db.Column(UUIDType, db.ForeignKey("vocabularies_metadata.id"))

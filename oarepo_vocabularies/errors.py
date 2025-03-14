from oarepo_runtime.i18n import lazy_gettext as _


class VocabularyTypeDoesNotExist(Exception):
    """The record is already in the community."""

    description = _("Vocabulary type does not exist.")

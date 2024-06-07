import typing

from flask import current_app
from werkzeug.local import LocalProxy

if typing.TYPE_CHECKING:
    from .ext import OARepoVocabularies
    from .services.cache import UIVocabularyCache
    from .services.service import VocabularyTypeService


def _ext_proxy(attr):
    return LocalProxy(
        lambda: getattr(current_app.extensions["oarepo-vocabularies"], attr)
    )


current_oarepo_vocabularies: "OARepoVocabularies" = LocalProxy(  # type: ignore
    lambda: current_app.extensions["oarepo-vocabularies"]
)

current_type_service: "VocabularyTypeService" = _ext_proxy("type_service")  # type: ignore
"""Proxy to the instantiated vocabulary type service."""

current_ui_vocabulary_cache: "UIVocabularyCache" = _ext_proxy("ui_cache")  # type: ignore

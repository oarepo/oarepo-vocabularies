from flask import current_app
from werkzeug.local import LocalProxy


def _ext_proxy(attr):
    return LocalProxy(
        lambda: getattr(current_app.extensions["oarepo-vocabularies"], attr)
    )


current_type_service = _ext_proxy("type_service")
"""Proxy to the instantiated vocabulary type service."""

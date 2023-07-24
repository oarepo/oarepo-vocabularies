from flask import current_app
from werkzeug.local import LocalProxy


def _ext_proxy(attr):
    return LocalProxy(
        lambda: getattr(current_app.extensions["oarepo-vocabularies-authorities"], attr)
    )


current_vocabularies_authorities = _ext_proxy("auth_getter")
"""Proxy to the instantiated vocabulary authorities."""

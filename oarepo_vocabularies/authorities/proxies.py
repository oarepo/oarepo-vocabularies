from flask import current_app
from werkzeug.local import LocalProxy

authorities = LocalProxy(
    lambda: current_app.extensions["oarepo-vocabularies-authorities"]
)

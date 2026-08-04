#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of oarepo-ui (see https://github.com/oarepo/oarepo-ui).
#
# oarepo-ui is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Decorators for content negotiation on vocabulary entries."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from flask import redirect, request
from invenio_base import invenio_url_for
from werkzeug.http import parse_accept_header

if TYPE_CHECKING:
    from werkzeug import Response


def vocabulary_content_negotiation[T: Callable](f: T) -> T:
    """Handle content negotiation.

     Handle content negotiation and redirect to appropriate URLs
    based on the "accept" header in the request and the record attributes. This ensures
    that requests expecting a vocabulary entry page are served directly, while others are redirected
    to specific API endpoints based on the vocabulary.
    """

    @wraps(f)
    def inner(*args: Any, **kwargs: Any) -> Response:
        parsed_accept_header = parse_accept_header(request.headers.get("accept", "text/html"))
        landing_page_accept_header_types = {"text/html", "application/xhtml+xml"}
        if parsed_accept_header.best_match(landing_page_accept_header_types):
            return f(*args, **kwargs)

        api_url = invenio_url_for("vocabularies.read", type=kwargs["vocabulary_type"], pid_value=kwargs["pid_value"])
        return redirect(api_url)

    return inner  # type: ignore[return-value]

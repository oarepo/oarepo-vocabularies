# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Validation of the urls used to reach the ORCID public data file.

The urls come from three places: the Figshare API responses, the application
configuration and the job arguments. All of them end up in ``requests``/``urllib``, so
they are validated first: only absolute ``https`` urls without embedded credentials are
accepted. That prevents a misconfigured or malicious source from making the worker fetch
``file://``, ``ftp://`` or plain ``http://`` resources.
"""

from __future__ import annotations

from urllib.parse import urlsplit

ALLOWED_SCHEME = "https"
"""The only url scheme allowed for outbound requests."""


class UnsafeUrlError(ValueError):
    """Raised when a url is not an absolute https url."""


def sanitize_url(url: object) -> str:
    """Return the url unchanged if it is a safe https url, raise otherwise.

    :param url: url to validate, as found in the configuration, in an API response or in
        the job arguments.
    :raises UnsafeUrlError: if the url is not an absolute https url without credentials.
    """
    if not isinstance(url, str) or not url:
        raise UnsafeUrlError("url must be a non-empty string")

    parts = urlsplit(url)
    if parts.scheme != ALLOWED_SCHEME:
        raise UnsafeUrlError(f"url must use the {ALLOWED_SCHEME} scheme, got {parts.scheme or 'no scheme'}: {url!r}")
    if not parts.hostname:
        raise UnsafeUrlError(f"url has no host: {url!r}")
    if parts.username is not None or parts.password is not None:
        raise UnsafeUrlError(f"url must not contain credentials: {url!r}")

    return url

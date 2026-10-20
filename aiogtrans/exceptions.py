from __future__ import annotations

from collections.abc import Sequence


class TranslationError(Exception):
    """Raised when a translation or detection request fails."""


class HTTPError(TranslationError):
    """Raised when the Google Translate API returns a non-2xx status code."""

    def __init__(self, status_code: int, service_urls: Sequence[str]) -> None:
        self.status_code = status_code
        super().__init__(f'Unexpected status code "{status_code}" from {service_urls}')

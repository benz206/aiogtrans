from __future__ import annotations


class TranslationError(Exception):
    """Raised when a translation or detection request fails."""


class HTTPError(TranslationError):
    """Raised when the Google Translate API returns a non-2xx status code."""

    def __init__(self, status_code: int, service_urls) -> None:
        self.status_code = status_code
        super().__init__(f'Unexpected status code "{status_code}" from {service_urls}')

"""
Async Google Translate client.
"""

from __future__ import annotations

import asyncio
import json
import random
import warnings
from collections.abc import Sequence
from types import TracebackType
from typing import Any

import httpx

from aiogtrans import urls
from aiogtrans.cache import Cache
from aiogtrans.constants import (
    DEFAULT_CLIENT_SERVICE_URLS,
    DEFAULT_RAISE_EXCEPTION,
    DEFAULT_USER_AGENT,
    LANGCODES,
    LANGUAGES,
    SPECIAL_CASES,
)
from aiogtrans.exceptions import HTTPError, TranslationError
from aiogtrans.models import Detected, Translated, TranslatedPart

RPC_ID = "MkEWBc"
RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class Translator:
    """
    Async client for the Google Translate Ajax API.

    Parameters
    ----------
    service_urls:
        One or more ``translate.google.*`` hostnames to use. A random one is
        chosen per request when multiple are provided.
    user_agent:
        ``User-Agent`` header value sent with every request.
    raise_exception:
        When ``True``, non-200 responses raise an :class:`HTTPError`.
        Defaults to ``False``.
    timeout:
        HTTP request timeout in seconds.
    use_fallback:
        Deprecated and ignored. It previously targeted
        ``translate.googleapis.com``, which rejects these requests.
    cache_capacity:
        Number of translation/detection results to cache in memory (LRU).
        ``0`` disables caching (default).
    retries:
        Number of HTTP attempts (on network errors and 429/5xx responses)
        before giving up.
        Defaults to ``3``.
    """

    def __init__(
        self,
        service_urls: Sequence[str] = DEFAULT_CLIENT_SERVICE_URLS,
        user_agent: str = DEFAULT_USER_AGENT,
        raise_exception: bool = DEFAULT_RAISE_EXCEPTION,
        timeout: int | float = 10.0,
        use_fallback: bool = False,
        cache_capacity: int = 0,
        retries: int = 3,
        _aclient: httpx.AsyncClient | None = None,
    ) -> None:
        self.raise_exception = raise_exception
        self.retries = retries
        self._cache: Cache | None = (
            Cache(cache_capacity) if cache_capacity > 0 else None
        )

        if use_fallback:
            warnings.warn(
                "use_fallback is deprecated and has no effect; the googleapis.com "
                "endpoint does not support this client's API.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.service_urls = service_urls
        self.client_type = "tw-ob"

        if _aclient is not None:
            self._aclient = _aclient
        else:
            headers = {
                "User-Agent": user_agent,
                "Referer": "https://translate.google.com",
            }
            self._aclient = httpx.AsyncClient(
                headers=headers, timeout=timeout, http2=True
            )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._aclient.aclose()

    async def __aenter__(self) -> Translator:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _pick_service_url(self) -> str:
        if len(self.service_urls) == 1:
            return self.service_urls[0]
        return random.choice(list(self.service_urls))

    def _build_rpc_request(self, text: str, dest: str, src: str) -> str:
        return json.dumps(
            [
                [
                    [
                        RPC_ID,
                        json.dumps(
                            [[text, src, dest, True], [None]], separators=(",", ":")
                        ),
                        None,
                        "generic",
                    ],
                ]
            ],
            separators=(",", ":"),
        )

    async def _translate(
        self, text: str, dest: str, src: str
    ) -> tuple[str, httpx.Response]:
        url = urls.TRANSLATE_RPC.format(host=self._pick_service_url())
        data = {"f.req": self._build_rpc_request(text, dest, src)}
        params: dict[str, str | int] = {
            "rpcids": RPC_ID,
            # NOTE: This build label is from 2020 and may become stale if Google
            # changes their API version checks. Update if translation stops working.
            "bl": "boq_translate-webserver_20201207.13_p0",
            "soc-app": 1,
            "soc-platform": 1,
            "soc-device": 1,
            "rt": "c",
        }

        last_exc: Exception | None = None
        response: httpx.Response | None = None
        for attempt in range(self.retries):
            try:
                response = await self._aclient.post(url, params=params, data=data)
            except Exception as exc:
                last_exc = exc
                response = None
            else:
                if response.status_code not in RETRY_STATUS_CODES:
                    break
            if attempt < self.retries - 1:
                await asyncio.sleep(2**attempt)

        if response is None:
            raise TranslationError(
                f"Request failed after {self.retries} attempts"
            ) from last_exc

        if response.status_code != 200 and self.raise_exception:
            raise HTTPError(response.status_code, self.service_urls)
        return response.text, response

    def _parse_response(self, data: str) -> str:
        """
        Extract the JSON blob that corresponds to *RPC_ID* from the raw
        streamed response returned by ``batchexecute``.
        """
        token_found = False
        square_bracket_counts = [0, 0]
        resp = ""

        for line in data.split("\n"):
            token_found = token_found or f'"{RPC_ID}"' in line[:30]
            if not token_found:
                continue

            is_in_string = False
            for index, char in enumerate(line):
                if char == '"' and line[max(0, index - 1)] != "\\":
                    is_in_string = not is_in_string
                if not is_in_string:
                    if char == "[":
                        square_bracket_counts[0] += 1
                    elif char == "]":
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break

        return resp

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def translate(
        self, text: str, dest: str = "en", src: str = "auto"
    ) -> Translated:
        """
        Translate *text* from *src* to *dest*.

        Parameters
        ----------
        text:
            Text to translate. Maximum 15 000 characters.
        dest:
            Destination language code or name (e.g. ``"en"``, ``"english"``).
        src:
            Source language code or name. ``"auto"`` triggers auto-detection.

        Returns
        -------
        Translated
        """
        if len(text) > 15000:
            raise ValueError(f"Text too long: {len(text)} characters (max 15 000)")

        dest = dest.lower().split("_", 1)[0]
        src = src.lower().split("_", 1)[0]

        if src != "auto" and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError(f"Invalid source language: {src!r}")

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError(f"Invalid destination language: {dest!r}")

        cache_key = f"{src}:{dest}:{text}"
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached  # type: ignore[return-value]

        origin = text
        raw, response = await self._translate(text, dest, src)
        resp = self._parse_response(raw)

        try:
            outer = json.loads(resp)
            parsed = json.loads(outer[0][2])
        except Exception as exc:
            raise TranslationError(
                f"Failed to parse translation response: {exc}\nResponse: {response}"
            ) from exc

        should_spacing: bool = parsed[1][0][0][3]
        translated_parts: list[TranslatedPart] = [
            TranslatedPart(part[0], (part[1] if len(part) >= 2 else None) or [])
            for part in parsed[1][0][0][5]
        ]
        translated = (" " if should_spacing else "").join(
            part.text for part in translated_parts
        )

        if src == "auto":
            try:
                src = parsed[2]
            except (IndexError, KeyError):
                pass
        if src == "auto":
            try:
                src = parsed[0][2]
            except (IndexError, KeyError):
                pass

        origin_pronunciation: str | None = None
        try:
            origin_pronunciation = parsed[0][0]
        except (IndexError, KeyError):
            pass

        pronunciation: str | None = None
        try:
            pronunciation = parsed[1][0][0][1]
        except (IndexError, KeyError):
            pass

        extra_data: dict[str, Any] = {
            "confidence": None,
            "parts": translated_parts,
            "origin_pronunciation": origin_pronunciation,
            "parsed": parsed,
        }

        result = Translated(
            src=src,
            dest=dest,
            origin=origin,
            text=translated,
            pronunciation=pronunciation,
            parts=translated_parts,
            extra_data=extra_data,
            response=response,
        )
        if self._cache is not None:
            self._cache.add(cache_key, result)
        return result

    async def detect(self, text: str) -> Detected:
        """
        Detect the language of *text*.

        Parameters
        ----------
        text:
            Text whose language should be identified.

        Returns
        -------
        Detected
        """
        cache_key = f"detect:{text}"
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached  # type: ignore[return-value]

        translated = await self.translate(text, src="auto", dest="en")
        result = Detected(
            lang=translated.src,
            confidence=translated.extra_data.get("confidence")
            if translated.extra_data
            else None,
            response=translated.response,
        )
        if self._cache is not None:
            self._cache.add(cache_key, result)
        return result

    async def translate_bulk(
        self,
        texts: list[str],
        dest: str = "en",
        src: str = "auto",
        concurrency: int = 10,
    ) -> list[Translated]:
        """Translate multiple texts concurrently, at most *concurrency* at a time."""
        semaphore = asyncio.Semaphore(concurrency)

        async def translate_one(text: str) -> Translated:
            async with semaphore:
                return await self.translate(text, dest=dest, src=src)

        return list(await asyncio.gather(*[translate_one(t) for t in texts]))

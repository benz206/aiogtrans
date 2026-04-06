"""
Copyright (c) 2022 Ben Z

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

from __future__ import annotations

from typing import Optional

import httpx


class Base:
    """Base class for response objects such as Translated and Detected."""

    __slots__ = ("_response",)

    def __init__(self, response: Optional[httpx.Response] = None) -> None:
        self._response = response


class TranslatedPart:
    """A single segment of a translated result with its translation candidates."""

    __slots__ = ("text", "candidates")

    def __init__(self, text: str, candidates: list[str]) -> None:
        self.text = text
        self.candidates = candidates

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"TranslatedPart(text={self.text!r}, candidates={self.candidates!r})"


class Translated(Base):
    """
    Result object returned by :meth:`Translator.translate`.

    Attributes
    ----------
    src:
        Detected or specified source language code.
    dest:
        Destination language code.
    origin:
        Original input text.
    text:
        Translated text.
    pronunciation:
        Romanised pronunciation of the translated text (may be ``None``).
    parts:
        List of :class:`TranslatedPart` segments.
    extra_data:
        Raw extra data extracted from the API response.
    """

    __slots__ = (
        "src",
        "dest",
        "origin",
        "text",
        "pronunciation",
        "extra_data",
        "parts",
    )

    def __init__(
        self,
        src: str,
        dest: str,
        origin: str,
        text: str,
        pronunciation: Optional[str],
        parts: list[TranslatedPart],
        extra_data: Optional[dict] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.src = src
        self.dest = dest
        self.origin = origin
        self.text = text
        self.pronunciation = pronunciation
        self.parts = parts
        self.extra_data = extra_data

    def __str__(self) -> str:
        return (
            f"Translated(src={self.src}, dest={self.dest}, text={self.text}, "
            f"pronunciation={self.pronunciation})"
        )

    def __repr__(self) -> str:
        return (
            f"Translated(src={self.src!r}, dest={self.dest!r}, origin={self.origin!r}, "
            f"text={self.text!r}, pronunciation={self.pronunciation!r})"
        )


class Detected(Base):
    """
    Result object returned by :meth:`Translator.detect`.

    Attributes
    ----------
    lang:
        Detected language code.
    confidence:
        Confidence score (``None`` if unavailable).
    """

    __slots__ = ("lang", "confidence")

    def __init__(self, lang: str, confidence: Optional[float], **kwargs) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        self.confidence = confidence

    def __str__(self) -> str:
        return f"Detected(lang={self.lang}, confidence={self.confidence})"

    def __repr__(self) -> str:
        return f"Detected(lang={self.lang!r}, confidence={self.confidence!r})"

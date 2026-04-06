"""Tests for the LRU Cache (aiogtrans.cache)."""

from __future__ import annotations

import pytest

from aiogtrans.cache import Cache
from aiogtrans.models import Detected, Translated, TranslatedPart


def _translated(text: str = "hello") -> Translated:
    return Translated(
        src="ko",
        dest="en",
        origin="안녕",
        text=text,
        pronunciation=None,
        parts=[TranslatedPart(text, [])],
        response=None,
    )


def _detected(lang: str = "ko") -> Detected:
    return Detected(lang=lang, confidence=None, response=None)


class TestCache:
    def test_get_missing_returns_none(self) -> None:
        cache = Cache()
        assert cache.get("nonexistent") is None

    def test_add_and_get(self) -> None:
        cache = Cache()
        obj = _translated()
        cache.add("hello", obj)
        assert cache.get("hello") is obj

    def test_len(self) -> None:
        cache = Cache()
        assert len(cache) == 0
        cache.add("a", _translated("a"))
        assert len(cache) == 1
        cache.add("b", _translated("b"))
        assert len(cache) == 2

    def test_contains(self) -> None:
        cache = Cache()
        cache.add("key", _translated())
        assert "key" in cache
        assert "missing" not in cache

    def test_evicts_oldest_when_over_capacity(self) -> None:
        cache = Cache(capacity=2)
        cache.add("a", _translated("a"))
        cache.add("b", _translated("b"))
        cache.add("c", _translated("c"))  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") is not None
        assert cache.get("c") is not None

    def test_lru_order_preserved_on_get(self) -> None:
        """Accessing an entry should move it to the end (most recently used)."""
        cache = Cache(capacity=2)
        cache.add("a", _translated("a"))
        cache.add("b", _translated("b"))
        # Access "a" so it becomes MRU; "b" becomes LRU
        cache.get("a")
        cache.add("c", _translated("c"))  # should evict "b"
        assert cache.get("b") is None
        assert cache.get("a") is not None

    def test_overwrite_existing_key(self) -> None:
        cache = Cache()
        cache.add("key", _translated("first"))
        cache.add("key", _translated("second"))
        result = cache.get("key")
        assert result is not None
        assert result.text == "second"

    def test_stores_detected_objects(self) -> None:
        cache = Cache()
        obj = _detected("ja")
        cache.add("detect:test", obj)
        assert cache.get("detect:test") is obj

    def test_capacity_one(self) -> None:
        cache = Cache(capacity=1)
        cache.add("a", _translated("a"))
        cache.add("b", _translated("b"))
        assert cache.get("a") is None
        assert cache.get("b") is not None

"""
LRU cache for translation and detection results.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Optional, Union

from .models import Detected, Translated


class Cache:
    """
    LRU cache for API call results.

    Two instances are typically created per :class:`~aiogtrans.Translator`:
    one for translations and one for detections.

    Parameters
    ----------
    capacity:
        Maximum number of entries before the oldest is evicted. Default 1 000.
    """

    def __init__(self, capacity: int = 1000) -> None:
        self._cache: OrderedDict[str, Union[Translated, Detected]] = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> Optional[Union[Translated, Detected]]:
        """Return the cached value for *key*, or ``None`` if not present."""
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def add(self, key: str, value: Union[Translated, Detected]) -> None:
        """Store *value* under *key*, evicting the oldest entry if over capacity."""
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache

"""
Free Google Translate API for Python. Translates totally free of charge.

Forked by _Leg3ndary after original project was abandoned.
"""

__all__ = (
    "Translator",
    "LANGCODES",
    "LANGUAGES",
    "Translated",
    "Detected",
    "TranslatedPart",
    "Cache",
    "HTTPError",
    "TranslationError",
)

from aiogtrans.client import Translator
from aiogtrans.constants import LANGCODES, LANGUAGES
from aiogtrans.models import Detected, Translated, TranslatedPart
from aiogtrans.cache import Cache
from aiogtrans.exceptions import HTTPError, TranslationError

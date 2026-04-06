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
)

from aiogtrans.client import Translator
from aiogtrans.constants import LANGCODES, LANGUAGES
from aiogtrans.models import Detected, Translated

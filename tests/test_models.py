"""Tests for model classes (aiogtrans.models)."""

from __future__ import annotations

from aiogtrans.models import Base, Detected, Translated, TranslatedPart


class TestTranslatedPart:
    def test_str(self) -> None:
        part = TranslatedPart("Hello", ["Hello", "Hi"])
        assert str(part) == "Hello"

    def test_repr(self) -> None:
        part = TranslatedPart("Hello", ["Hello"])
        assert "Hello" in repr(part)
        assert "TranslatedPart" in repr(part)

    def test_candidates(self) -> None:
        part = TranslatedPart("Hola", ["Hola", "Buenos días"])
        assert part.candidates == ["Hola", "Buenos días"]

    def test_empty_candidates(self) -> None:
        part = TranslatedPart("Hello", [])
        assert part.candidates == []


class TestTranslated:
    def _make(self, **kwargs) -> Translated:
        defaults = dict(
            src="ko",
            dest="en",
            origin="안녕하세요.",
            text="Good evening.",
            pronunciation="Good evening.",
            parts=[TranslatedPart("Good evening.", ["Good evening."])],
            extra_data=None,
            response=None,
        )
        defaults.update(kwargs)
        return Translated(**defaults)

    def test_str(self) -> None:
        t = self._make()
        s = str(t)
        assert "Translated" in s
        assert "ko" in s
        assert "en" in s

    def test_repr(self) -> None:
        t = self._make()
        assert "Translated" in repr(t)

    def test_optional_pronunciation(self) -> None:
        t = self._make(pronunciation=None)
        assert t.pronunciation is None

    def test_optional_extra_data(self) -> None:
        t = self._make(extra_data=None)
        assert t.extra_data is None

    def test_fields(self) -> None:
        t = self._make()
        assert t.src == "ko"
        assert t.dest == "en"
        assert t.origin == "안녕하세요."
        assert t.text == "Good evening."


class TestDetected:
    def test_str(self) -> None:
        d = Detected(lang="ko", confidence=0.95, response=None)
        s = str(d)
        assert "Detected" in s
        assert "ko" in s

    def test_repr(self) -> None:
        d = Detected(lang="ko", confidence=0.95, response=None)
        assert "Detected" in repr(d)

    def test_none_confidence(self) -> None:
        d = Detected(lang="ko", confidence=None, response=None)
        assert d.confidence is None

    def test_response_stored(self) -> None:
        d = Detected(lang="en", confidence=0.5, response=None)
        assert d._response is None


class TestBase:
    def test_slots(self) -> None:
        b = Base(response=None)
        assert b._response is None

    def test_no_instance_dict(self) -> None:
        """__slots__ should prevent an instance __dict__."""
        b = Base()
        assert not hasattr(b, "__dict__")

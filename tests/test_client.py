"""Tests for Translator (aiogtrans.client)."""

from __future__ import annotations

import pytest

from aiogtrans import Translator
from aiogtrans.models import Detected, Translated, TranslatedPart

from .conftest import make_mock_client, make_rpc_response


# ---------------------------------------------------------------------------
# translate()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_translate_basic() -> None:
    """translate() returns a Translated object with correct fields."""
    response_text = make_rpc_response("Good evening.", src_lang="ko", pronunciation="Good evening.")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.translate("안녕하세요.", dest="en")

    assert isinstance(result, Translated)
    assert result.dest == "en"
    assert result.src == "ko"
    assert result.text == "Good evening."
    assert result.origin == "안녕하세요."


@pytest.mark.asyncio
async def test_translate_pronunciation() -> None:
    """translate() captures pronunciation when present."""
    response_text = make_rpc_response(
        "こんにちは。",
        src_lang="ko",
        pronunciation="Kon'nichiwa.",
    )
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.translate("안녕하세요.", dest="ja")

    assert result.pronunciation == "Kon'nichiwa."


@pytest.mark.asyncio
async def test_translate_parts() -> None:
    """translate() populates the parts list correctly."""
    response_text = make_rpc_response("Hello", src_lang="es")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.translate("Hola", src="es", dest="en")

    assert len(result.parts) == 1
    assert isinstance(result.parts[0], TranslatedPart)
    assert result.parts[0].text == "Hello"


@pytest.mark.asyncio
async def test_translate_explicit_src() -> None:
    """translate() accepts an explicit source language code."""
    response_text = make_rpc_response("The truth is my light", src_lang="la")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.translate("veritas lux mea", src="la", dest="en")

    assert result.src == "la"
    assert result.text == "The truth is my light"


@pytest.mark.asyncio
async def test_translate_language_name_as_dest() -> None:
    """translate() resolves a full language name (e.g. 'english') to its code."""
    response_text = make_rpc_response("Hello", src_lang="es")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.translate("Hola", src="es", dest="english")

    assert result.dest == "en"


@pytest.mark.asyncio
async def test_translate_invalid_dest_raises() -> None:
    """translate() raises ValueError for an unrecognised destination language."""
    translator = Translator(_aclient=make_mock_client(""))

    with pytest.raises(ValueError, match="Invalid destination language"):
        await translator.translate("hello", dest="xx_invalid")


@pytest.mark.asyncio
async def test_translate_invalid_src_raises() -> None:
    """translate() raises ValueError for an unrecognised source language."""
    translator = Translator(_aclient=make_mock_client(""))

    with pytest.raises(ValueError, match="Invalid source language"):
        await translator.translate("hello", src="xx_invalid")


@pytest.mark.asyncio
async def test_translate_spacing() -> None:
    """translate() joins parts with a space when should_spacing is True."""
    import json
    from tests.conftest import RPC_ID

    parts = [["Hello", ["Hello"]], ["world", ["world"]]]
    inner = [
        [None],
        [[[None, None, None, True, None, parts]]],
        "es",
    ]
    inner_str = json.dumps(inner, separators=(",", ":"))
    outer = [[RPC_ID, None, inner_str, None, None]]
    response_text = ")]}'" + "\n\n" + json.dumps(outer, separators=(",", ":")) + "\n"

    translator = Translator(_aclient=make_mock_client(response_text))
    result = await translator.translate("Hola mundo", src="es", dest="en")

    assert result.text == "Hello world"


# ---------------------------------------------------------------------------
# detect()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_detect_basic() -> None:
    """detect() returns a Detected object with the correct language code."""
    response_text = make_rpc_response("Hello", src_lang="ko")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.detect("안녕하세요.")

    assert isinstance(result, Detected)
    assert result.lang == "ko"


@pytest.mark.asyncio
async def test_detect_confidence_none() -> None:
    """detect() returns confidence=None since the API no longer provides it."""
    response_text = make_rpc_response("Hello", src_lang="ko")
    translator = Translator(_aclient=make_mock_client(response_text))

    result = await translator.detect("안녕하세요.")

    assert result.confidence is None


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_context_manager_closes_client() -> None:
    """Translator used as async context manager calls close() on exit."""
    mock_client = make_mock_client(make_rpc_response("Hello", src_lang="es"))

    async with Translator(_aclient=mock_client) as translator:
        assert translator is not None

    mock_client.aclose.assert_awaited_once()


# ---------------------------------------------------------------------------
# raise_exception flag
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_raise_exception_on_non_200() -> None:
    """raise_exception=True causes an Exception on non-200 status codes."""
    translator = Translator(
        _aclient=make_mock_client("", status_code=429),
        raise_exception=True,
    )

    with pytest.raises(Exception, match="429"):
        await translator.translate("hello", dest="en")


@pytest.mark.asyncio
async def test_no_raise_on_non_200_by_default() -> None:
    """raise_exception=False (default) does not raise on non-200 status."""
    # The response body is empty so JSON parsing will fail — we just want to
    # confirm that the HTTP status itself does NOT raise.
    translator = Translator(
        _aclient=make_mock_client("", status_code=429),
        raise_exception=False,
    )

    with pytest.raises(Exception, match="Failed to parse"):
        await translator.translate("hello", dest="en")

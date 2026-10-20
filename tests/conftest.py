"""Shared fixtures and helpers for the aiogtrans test suite."""

from __future__ import annotations

import json
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from aiogtrans.client import RPC_ID


def make_rpc_response(
    translated_text: str,
    src_lang: str = "ko",
    pronunciation: Optional[str] = None,
    origin_pronunciation: Optional[str] = None,
    should_spacing: bool = False,
) -> str:
    """
    Build a minimal fake Google Translate batchexecute response.

    The structure mirrors what the real API returns so that
    ``Translator._parse_response`` and the JSON parsing in ``translate()``
    both work without modification.
    """
    parts = [[translated_text, [translated_text]]]

    # Structure mirrors the real Google Translate batchexecute response.
    # client.py accesses: parsed[1][0][0][1] (pronunciation),
    #                     parsed[1][0][0][3] (should_spacing),
    #                     parsed[1][0][0][5] (parts)
    inner = [
        [origin_pronunciation],                                 # [0]
        [[[None, pronunciation, None, should_spacing, None, parts]]],  # [1][0][0]
        src_lang,                                               # [2]
    ]

    inner_str = json.dumps(inner, separators=(",", ":"))
    # Google batchexecute format: [rpcid, null, inner_json_str, null, null]
    # client.py reads data[0][2] for the inner JSON string.
    outer = [[RPC_ID, None, inner_str, None, None]]
    outer_str = json.dumps(outer, separators=(",", ":"))

    # The real response starts with )]}'\n\n before the JSON payload.
    return ")]}'" + "\n\n" + outer_str + "\n"


def make_mock_client(response_text: str, status_code: int = 200) -> httpx.AsyncClient:
    """Return an AsyncClient whose ``post`` method returns a fake response."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = status_code
    mock_response.text = response_text

    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()
    return mock_client


# Captured from a live translate.google.com response (eo -> en) in 2026. Note the
# spelling suggestion at [0][1] and the null candidates in each part.
REAL_EO_PARSED = [
    [None, [[[None, "<b><i>Tu</i></b> frazo estas skribita en Esperanto."], None, 2, [1], "Tu frazo estas skribita en Esperanto."]], "eo", [[[0, [[[None, 38]], [True]]]], 38], None, None, ["Tiu frazo estas skribita en Esperanto.", "auto", "en", True]],
    [[[None, None, None, None, None, [["That sentence is written in Esperanto.", None, None, None, None, None, "Tiu frazo estas skribita en Esperanto.", 1]], None, None, None, []]], "en", 1, "eo", ["Tiu frazo estas skribita en Esperanto.", "auto", "en", True]],
    "eo", None, None, None, None, [[[0], [[6, 1]]]],
]


def make_real_response(parsed: list) -> str:
    """Wrap *parsed* in the envelope that batchexecute actually returns."""
    inner_str = json.dumps(parsed, separators=(",", ":"))
    outer = [["wrb.fr", RPC_ID, inner_str, None, None, None, "generic"], ["di", 876]]
    outer_str = json.dumps(outer, separators=(",", ":"))
    return f")]}}'\n\n{len(outer_str)}\n{outer_str}\n25\n[[\"e\",4,null,null,414]]\n"

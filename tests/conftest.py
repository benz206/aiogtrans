"""Shared fixtures and helpers for the aiogtrans test suite."""

from __future__ import annotations

import json
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

RPC_ID = "MkEWBc"


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

"""Tests for the command-line entry point (aiogtrans.__main__)."""

from __future__ import annotations

import sys

import pytest

import aiogtrans.__main__ as cli
from aiogtrans import Translator

from .conftest import make_mock_client, make_rpc_response


def test_main_runs_translation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The console-script entry point is synchronous and prints the translation."""
    response_text = make_rpc_response("The truth is my light", src_lang="la")
    monkeypatch.setattr(
        cli, "Translator", lambda: Translator(_aclient=make_mock_client(response_text))
    )
    monkeypatch.setattr(sys, "argv", ["aiogtrans", "veritas lux mea", "-s", "la"])

    cli.main()

    assert "The truth is my light" in capsys.readouterr().out

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def block_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make any accidental network access fail the test immediately."""

    def blocked_connection(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Automated tests must not access the live network.")

    monkeypatch.setattr(socket, "create_connection", blocked_connection)


@pytest.fixture
def load_fixture() -> Any:
    fixture_dir = Path(__file__).parent / "fixtures"

    def _load(name: str) -> dict[str, Any]:
        with (fixture_dir / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)

    return _load

"""Focused tests for the planted regeneration key."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_fvsbc_regeneration.py"


class RegenModule(Protocol):
    """The subset of the regeneration helper these tests exercise."""

    def _key_text(self, *, au: int, species: str, site_index: float) -> str:
        """Return the raw FVS key."""
        ...


def _load_module() -> RegenModule:
    spec = importlib.util.spec_from_file_location("gavin_regen", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(RegenModule, module)


def test_regen_key_contains_planting() -> None:
    """The key has NOTREES, ESTAB, and a PLANT line."""
    module = _load_module()
    key = module._key_text(au=2, species="FD", site_index=100.0)
    assert "NOTREES" in key
    assert "ESTAB" in key
    assert "PLANT" in key
    assert "AU2 planted regeneration" in key

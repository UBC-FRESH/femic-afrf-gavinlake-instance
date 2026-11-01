"""Focused tests for the ws4 state-graph compiler."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pytest

pytest.importorskip("ws4.model.schema")
pytest.importorskip("pandas")

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_ws4_state_graph.py"


class StateGraphModule(Protocol):
    """The subset of the state-graph compiler these tests exercise."""

    def _constant_curve(
        self,
        *,
        curve_id: int,
        x_values: list[float],
        value: float,
    ) -> tuple[list[dict[str, float | int]], int]:
        """Return a constant curve and the next curve id."""
        ...


def _load_module() -> StateGraphModule:
    spec = importlib.util.spec_from_file_location("gavin_ws4_state_graph", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(StateGraphModule, module)


def test_constant_curve_repeats_value_and_advances_id() -> None:
    """The constant curve has one row per age and returns the next curve id."""
    module = _load_module()
    rows, next_id = module._constant_curve(
        curve_id=7,
        x_values=[60.0, 70.0],
        value=1.0,
    )
    assert next_id == 8
    assert [row["curve_id"] for row in rows] == [7, 7]
    assert [row["x"] for row in rows] == [60.0, 70.0]
    assert [row["y"] for row in rows] == [1.0, 1.0]

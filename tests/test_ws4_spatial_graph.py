"""Focused tests for the spatial state-graph helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pytest

pytest.importorskip("ws4.model.schema")
pytest.importorskip("geopandas")
pytest.importorskip("pandas")

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_ws4_spatial_graph.py"


class SpatialModule(Protocol):
    """The subset of the spatial compiler these tests exercise."""

    def _constant_curve(
        self,
        curve_id: int,
        x_values: list[float],
        value: float,
    ) -> tuple[list[dict[str, float | int]], int]:
        """Return a constant curve and the next curve id."""
        ...


def _load_module() -> SpatialModule:
    spec = importlib.util.spec_from_file_location("gavin_ws4_spatial", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(SpatialModule, module)


def test_constant_curve_repeats_value_and_advances_id() -> None:
    """The spatial helper builds one constant row per age."""
    module = _load_module()
    rows, next_id = module._constant_curve(5, [50.0, 60.0], 1.0)
    assert next_id == 6
    assert [row["curve_id"] for row in rows] == [5, 5]
    assert [row["x"] for row in rows] == [50.0, 60.0]

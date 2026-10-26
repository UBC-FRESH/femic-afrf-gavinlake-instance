"""Focused tests for the Gavin Lake baseline schedule helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import numpy as np

MODULE_PATH = Path(__file__).resolve().parents[1] / "ws4" / "build_baseline_schedule.py"


class BaselineModule(Protocol):
    """The subset of the baseline helper these tests exercise."""

    def interp_value(self, xs: np.ndarray, ys: np.ndarray, age: float) -> float:
        """Return a curve value at an age."""
        ...

    def entry_chain(
        self,
        *,
        track_id: int,
        age0: int,
        first_offset: int,
        area_ha: float,
        years: int,
        min_age: int,
        treatment: str,
        product_curve_ids: dict[int, int],
        transition_map: dict[int, tuple[int, int, int]],
        curves: dict[int, tuple[np.ndarray, np.ndarray]],
    ) -> list[tuple[int, float]]:
        """Return the treatment offsets and volumes for one block."""
        ...


def _load_module() -> BaselineModule:
    """Load the baseline helper by path without importing the ws4 package."""
    spec = importlib.util.spec_from_file_location("gavin_baseline", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(BaselineModule, module)


def test_interp_value_clamps_and_interpolates() -> None:
    """The curve reader clamps outside the domain and interpolates inside it."""
    module = _load_module()
    xs = np.array([80.0, 90.0])
    ys = np.array([100.0, 200.0])
    assert module.interp_value(xs, ys, 70.0) == 100.0
    assert module.interp_value(xs, ys, 85.0) == 150.0
    assert module.interp_value(xs, ys, 95.0) == 200.0


def test_entry_chain_repeats_at_the_minimum_age() -> None:
    """A block is re-entered every minimum-age interval on the new track."""
    module = _load_module()
    curves = {
        1: (np.array([80.0, 90.0]), np.array([10.0, 20.0])),
        2: (np.array([80.0, 90.0]), np.array([30.0, 40.0])),
    }
    entries = module.entry_chain(
        track_id=1,
        age0=70,
        first_offset=10,
        area_ha=2.0,
        years=200,
        min_age=80,
        treatment="CC",
        product_curve_ids={1: 1, 2: 2},
        transition_map={1: (2, 80, 998), 2: (2, 80, 998)},
        curves=curves,
    )
    assert [entry[0] for entry in entries] == [10, 90, 170]
    assert entries[0][1] == 20.0
    assert entries[1][1] == 60.0

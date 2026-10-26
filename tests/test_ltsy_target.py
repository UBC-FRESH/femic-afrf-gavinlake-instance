"""Focused tests for the Gavin Lake LTSY estimator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import numpy as np
import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "ws4" / "estimate_ltsy_target.py"


class LtsyModule(Protocol):
    """The subset of the LTSY estimator these tests exercise."""

    def interp_value(self, xs: np.ndarray, ys: np.ndarray, age: float) -> float:
        """Return a curve value at an age."""
        ...

    def mean_yield_curve(
        self,
        *,
        fragments: pd.DataFrame,
        curve_ids: dict[int, int],
        curves: dict[int, tuple[np.ndarray, np.ndarray]],
        max_age: int,
    ) -> pd.DataFrame:
        """Return the area-weighted mean yield curve."""
        ...

    def ltsy_from_curve(
        self,
        curve: pd.DataFrame,
        *,
        area_ha: float,
        period_width: int,
        uplift: float,
    ) -> dict[str, float | int]:
        """Return the CMAI and first-guess target."""
        ...


def _load_module() -> LtsyModule:
    """Load the LTSY estimator by path without importing the ws4 package."""
    spec = importlib.util.spec_from_file_location("gavin_ltsy", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(LtsyModule, module)


def test_interp_value_clamps_and_interpolates() -> None:
    """The curve reader clamps outside the domain and interpolates inside it."""
    module = _load_module()
    xs = np.array([0.0, 10.0])
    ys = np.array([0.0, 100.0])
    assert module.interp_value(xs, ys, 5.0) == 50.0
    assert module.interp_value(xs, ys, -1.0) == 0.0
    assert module.interp_value(xs, ys, 11.0) == 100.0


def test_mean_yield_curve_is_area_weighted() -> None:
    """The mean curve weights each track by its fragment area."""
    module = _load_module()
    fragments = pd.DataFrame({"TRACK": [1, 2], "AREA_HA": [1.0, 3.0]})
    curves = {
        1: (np.array([0.0, 10.0]), np.array([0.0, 10.0])),
        2: (np.array([0.0, 10.0]), np.array([0.0, 20.0])),
    }
    curve = module.mean_yield_curve(
        fragments=fragments,
        curve_ids={1: 1, 2: 2},
        curves=curves,
        max_age=10,
    )
    row = curve.loc[curve["age"] == 5].iloc[0]
    assert row["mean_yield_m3_ha"] == 8.75
    assert row["mai_m3_ha_yr"] == 1.75


def test_ltsy_from_curve_uses_cmai_and_uplift() -> None:
    """The first guess is CMAI times area times period width times uplift."""
    module = _load_module()
    curve = pd.DataFrame(
        {
            "age": [1, 10, 20],
            "mean_yield_m3_ha": [1.0, 50.0, 80.0],
            "mai_m3_ha_yr": [1.0, 5.0, 4.0],
        }
    )
    result = module.ltsy_from_curve(curve, area_ha=100.0, period_width=10, uplift=1.1)
    assert result["cmai_m3_ha_yr"] == 5.0
    assert result["cmai_age_years"] == 10
    assert result["ltsy_annual_m3"] == 500.0
    assert result["ltsy_period_m3"] == 5000.0
    assert result["first_guess_period_target_m3"] == 5500.0

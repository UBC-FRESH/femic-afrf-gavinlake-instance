"""Focused tests for the legacy-curve comparison helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_fvsbc_legacy_comparison.py"
)


class LegacyModule(Protocol):
    """The subset of the comparison helper these tests exercise."""

    def interpolate_curve(self, curve: pd.DataFrame, *, age: float) -> float:
        """Return an interpolated curve value."""
        ...


def _load_module() -> LegacyModule:
    spec = importlib.util.spec_from_file_location("gavin_fvsbc_legacy", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(LegacyModule, module)


def test_interpolate_curve_clamps_outside_domain() -> None:
    """The legacy interpolation returns NaN outside the curve domain."""
    module = _load_module()
    curve = pd.DataFrame({"x": [80.0, 100.0], "y": [200.0, 300.0]})
    assert module.interpolate_curve(curve, age=90.0) == 250.0
    assert module.interpolate_curve(curve, age=70.0) != module.interpolate_curve(curve, age=70.0)
    assert module.interpolate_curve(curve, age=110.0) != module.interpolate_curve(curve, age=110.0)

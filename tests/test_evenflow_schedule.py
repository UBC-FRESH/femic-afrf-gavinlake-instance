"""Focused tests for the even-flow schedule helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_evenflow_schedule.py"


class ScheduleModule(Protocol):
    """The subset of the schedule helper these tests exercise."""

    def _curve_value(self, curve: pd.DataFrame, x: float) -> float:
        """Return a curve value."""
        ...

    def greedy_schedule(self, volumes: pd.DataFrame) -> pd.DataFrame:
        """Return a block schedule."""
        ...


def _load_module() -> ScheduleModule:
    spec = importlib.util.spec_from_file_location("gavin_evenflow", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(ScheduleModule, module)


def test_curve_value_clamps_outside_domain() -> None:
    """A value outside the cut-curve domain is zero."""
    module = _load_module()
    curve = pd.DataFrame({"x": [60.0, 70.0], "y": [10.0, 20.0]})
    assert module._curve_value(curve, 65.0) == 15.0
    assert module._curve_value(curve, 50.0) == 0.0
    assert module._curve_value(curve, 80.0) == 0.0


def test_greedy_schedule_balances_two_blocks() -> None:
    """Two equal blocks go to different periods."""
    module = _load_module()
    volumes = pd.DataFrame(
        {
            "block_id": [1, 1, 2, 2],
            "offset": [0, 10, 0, 10],
            "volume_m3": [10.0, 10.0, 10.0, 10.0],
        }
    )
    schedule = module.greedy_schedule(volumes)
    assert set(schedule["offset"]) == {0, 10}

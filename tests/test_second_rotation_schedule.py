"""Focused tests for the 200-year rotation schedule."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_second_rotation_schedule.py"
)


class ScheduleModule(Protocol):
    """The subset of the 200-year helper these tests exercise."""

    def greedy_200_year(
        self,
        first: pd.DataFrame,
        second: pd.Series,
    ) -> pd.DataFrame:
        """Return the 200-year block schedule."""
        ...


def _load_module() -> ScheduleModule:
    spec = importlib.util.spec_from_file_location("gavin_200_year", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(ScheduleModule, module)


def test_200_year_schedule_has_two_entries_per_block() -> None:
    """A block gets one first and one second cut."""
    module = _load_module()
    first = pd.DataFrame(
        {
            "block_id": [1, 1],
            "offset": [0, 10],
            "volume_m3": [100.0, 100.0],
        }
    )
    second = pd.Series({1: 50.0})
    table = module.greedy_200_year(first, second)
    assert len(table) == 1
    assert table.iloc[0]["first_volume_m3"] == 100.0
    assert table.iloc[0]["second_volume_m3"] == 50.0
    assert table.iloc[0]["second_period"] == table.iloc[0]["first_period"] + 80

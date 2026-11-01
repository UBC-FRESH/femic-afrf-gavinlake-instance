"""Focused tests for the second-rotation test."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_second_rotation_test.py"


class SecondModule(Protocol):
    """The subset of the second-rotation helper these tests exercise."""

    def second_rotation_table(
        self,
        schedule: pd.DataFrame,
        *,
        area_by_block: pd.Series,
        au_by_block: pd.Series,
        regen: pd.DataFrame,
    ) -> pd.DataFrame:
        """Return second-rotation volume by block."""
        ...


def _load_module() -> SecondModule:
    spec = importlib.util.spec_from_file_location("gavin_second", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(SecondModule, module)


def test_second_rotation_uses_age80_volume() -> None:
    """The second harvest is area times the age-80 regeneration volume."""
    module = _load_module()
    schedule = pd.DataFrame(
        {"block_id": [1], "treatment": ["CLEARCUT_E0"], "offset": [0], "estimated_volume_m3": [1.0]}
    )
    regen = pd.DataFrame({"au": [1, 1], "Year": [0, 80], "MCuM": [0.0, 300.0]})
    table = module.second_rotation_table(
        schedule,
        area_by_block=pd.Series({1: 2.0}),
        au_by_block=pd.Series({1: 1.0}),
        regen=regen,
    )
    assert table.iloc[0]["second_rotation_m3"] == 600.0
    assert table.iloc[0]["second_period"] == 80

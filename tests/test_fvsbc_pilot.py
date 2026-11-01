"""Focused tests for the Gavin Lake FVS-BC pilot helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("geopandas")

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_fvsbc_pilot.py"


class PilotModule(Protocol):
    """The subset of the pilot these tests exercise."""

    def _density_plan(self, target_tph: float) -> tuple[int, int]:
        """Return sample size and expansion."""
        ...

    def _initial_ba(self, records: list[dict[str, float | int | str]]) -> float:
        """Return initial basal area."""
        ...

    def _species_pool(self, shares: dict[str, float]) -> tuple[list[str], np.ndarray]:
        """Return species codes and probabilities."""
        ...

    def _tree_records(
        self,
        sample: pd.DataFrame,
        species: list[str],
        *,
        expansion: int,
        age: float,
    ) -> list[dict[str, float | int | str]]:
        """Return FVS tree records."""
        ...


def _load_module() -> PilotModule:
    spec = importlib.util.spec_from_file_location("gavin_fvsbc_pilot", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(PilotModule, module)


def test_density_plan_keeps_expansion_integral() -> None:
    """The plan reproduces the target density with an integer expansion."""
    module = _load_module()
    sample, expansion = module._density_plan(85.0)
    assert sample == 85
    assert expansion == 1
    sample, expansion = module._density_plan(594.0)
    assert sample == 59
    assert expansion == 10
    assert sample * expansion == 590


def test_species_pool_maps_vri_codes() -> None:
    """VRI species shares map to BC codes and normalize."""
    module = _load_module()
    codes, probabilities = module._species_pool({"FD": 0.5, "SX": 0.25, "CW": 0.25})
    assert codes == ["FD", "SE", "CW"]
    assert abs(float(probabilities[0]) - 0.5) < 1e-12


def test_initial_ba_uses_expanded_diameter() -> None:
    """A 100 cm tree with count one contributes 0.7854 m2/ha."""
    module = _load_module()
    records: list[dict[str, float | int | str]] = [{"diam": 100.0, "tree_count": 1.0}]
    assert abs(module._initial_ba(records) - 0.7853981633974483) < 1e-12


def test_tree_records_carry_species_and_density() -> None:
    """Tree records preserve species, DBH, height, and expansion."""
    module = _load_module()
    sample = pd.DataFrame(
        {
            "dbh_cm_est": [10.0, 20.0],
            "height_m": [8.0, 15.0],
        }
    )
    records = module._tree_records(sample, ["FD", "CW"], expansion=3, age=80.0)
    assert [record["species"] for record in records] == ["FD", "CW"]
    assert [record["tree_count"] for record in records] == [3.0, 3.0]
    assert [record["tree_age"] for record in records] == [80.0, 80.0]

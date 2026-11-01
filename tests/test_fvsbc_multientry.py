"""Focused tests for the second-entry FVS helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_fvsbc_multientry.py"


class MultiEntryModule(Protocol):
    """The subset of the multi-entry helper these tests exercise."""

    def _tree_records(
        self,
        tree_list: pd.DataFrame,
        *,
        age: float,
    ) -> tuple[list[dict[str, float | int | str]], float]:
        """Return tree records and initial BA."""
        ...


def _load_module() -> MultiEntryModule:
    spec = importlib.util.spec_from_file_location("gavin_fvsbc_multientry", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(MultiEntryModule, module)


def test_second_entry_records_group_by_tree_id() -> None:
    """Split FVS records collapse into one tree with summed TPH."""
    module = _load_module()
    tree_list = pd.DataFrame(
        {
            "TreeId": ["A", "A", "B"],
            "TPH": [1.0, 2.0, 3.0],
            "DBH": [20.0, 22.0, 30.0],
            "Ht": [15.0, 16.0, 20.0],
            "SpeciesFVS": ["FD", "FD", "CW"],
            "PctCr": [45.0, 45.0, 55.0],
        }
    )
    records, ba = module._tree_records(tree_list, age=80.0)
    assert len(records) == 2
    assert records[0]["tree_count"] == 3
    assert records[0]["tree_age"] == 80.0
    assert ba > 0.0

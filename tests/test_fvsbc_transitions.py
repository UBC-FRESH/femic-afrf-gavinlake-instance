"""Focused tests for the FVS-BC transition compiler."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, cast

import pandas as pd

MODULE_PATH = Path(__file__).resolve().parents[1] / "runbooks" / "build_gl_fvsbc_transitions.py"


class TransitionModule(Protocol):
    """The subset of the transition compiler these tests exercise."""

    def dbh_class(self, dbh_cm: float) -> int:
        """Return the DBH class."""
        ...

    def collapse_tree_ids(self, trees: pd.DataFrame) -> pd.DataFrame:
        """Collapse split tree records."""
        ...

    def distribution_frame(self, trees: pd.DataFrame) -> pd.DataFrame:
        """Return DBH distributions."""
        ...

    def transition_frame(
        self,
        trees: pd.DataFrame,
        cuts: pd.DataFrame,
    ) -> pd.DataFrame:
        """Return class transitions."""
        ...


def _load_module() -> TransitionModule:
    spec = importlib.util.spec_from_file_location("gavin_fvsbc_transitions", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The module is loaded by path, so mypy cannot see its static type.
    return cast(TransitionModule, module)


def test_dbh_class_bins_and_caps() -> None:
    """DBH classes are 5 cm bins capped at 100 cm."""
    module = _load_module()
    assert module.dbh_class(0.0) == 0
    assert module.dbh_class(12.4) == 10
    assert module.dbh_class(100.0) == 100
    assert module.dbh_class(145.0) == 100


def test_collapse_tree_ids_combines_split_records() -> None:
    """Split records with one TreeId are one tree with a weighted DBH."""
    module = _load_module()
    trees = pd.DataFrame(
        {
            "au": [1, 1],
            "treatment": ["ct60", "ct60"],
            "Year": [10, 10],
            "TreeId": ["A", "A"],
            "DBH": [10.0, 20.0],
            "TPH": [1.0, 1.0],
            "MCuM": [1.0, 3.0],
        }
    )
    collapsed = module.collapse_tree_ids(trees)
    assert len(collapsed) == 1
    assert collapsed.iloc[0]["TPH"] == 2.0
    assert collapsed.iloc[0]["DBH"] == 15.0
    assert collapsed.iloc[0]["MCuM"] == 4.0


def test_distribution_sums_tph_by_class() -> None:
    """Distribution rows aggregate TPH and volume by DBH class."""
    module = _load_module()
    trees = pd.DataFrame(
        {
            "au": [1, 1],
            "treatment": ["untreated", "untreated"],
            "Year": [0, 0],
            "TreeId": ["A", "B"],
            "DBH": [10.0, 12.0],
            "TPH": [2.0, 3.0],
            "MCuM": [1.0, 2.0],
        }
    )
    distribution = module.distribution_frame(trees)
    assert len(distribution) == 1
    assert distribution.iloc[0]["tph"] == 5.0
    assert distribution.iloc[0]["volume_m3"] == 3.0


def test_transitions_label_live_harvest_and_mortality() -> None:
    """A surviving tree is live; missing trees are harvest or mortality."""
    module = _load_module()
    trees = pd.DataFrame(
        {
            "au": [1, 1, 1, 2, 2, 2],
            "treatment": ["ct60", "ct60", "ct60", "untreated", "untreated", "untreated"],
            "Year": [0, 10, 0, 0, 0, 10],
            "TreeId": ["A", "A", "B", "C", "D", "E"],
            "DBH": [10.0, 12.0, 20.0, 30.0, 40.0, 8.0],
            "TPH": [2.0, 2.0, 1.0, 1.0, 1.0, 1.0],
            "MCuM": [1.0, 2.0, 1.0, 1.0, 1.0, 0.1],
        }
    )
    cuts = pd.DataFrame(
        {
            "au": [1],
            "treatment": ["ct60"],
            "Year": [0],
            "TreeId": ["B"],
        }
    )
    transitions = module.transition_frame(trees, cuts)
    fates = {(str(row.au), str(row.fate)) for row in transitions.itertuples(index=False)}
    assert ("1", "live") in fates
    assert ("1", "harvest") in fates
    assert ("2", "mortality") in fates
    harvest = transitions[(transitions["au"] == 1) & (transitions["fate"] == "harvest")]
    mortality = transitions[(transitions["au"] == 2) & (transitions["fate"] == "mortality")]
    assert harvest["tph"].sum() == 1.0
    assert mortality["tph"].sum() == 2.0

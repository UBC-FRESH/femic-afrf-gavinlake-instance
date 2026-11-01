#!/usr/bin/env python3
"""Compile DBH distributions and ten-year transitions from the FVS-BC pilot.

The pilot writes one tree list per AU and treatment for every ten-year cycle.
This script turns those tree lists into:

- a DBH-class distribution by AU, treatment, and year;
- a ten-year transition table by AU, treatment, DBH class, and fate.

A tree that is present in the next cycle is ``live``. A tree absent from the
next cycle is ``harvest`` when the cut list names it, and ``mortality``
otherwise.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

#: DBH class width in centimetres.
DBH_CLASS_WIDTH: int = 5

#: Last DBH class lower bound; all larger trees are pooled.
DBH_CLASS_MAX: int = 100


def dbh_class(dbh_cm: float) -> int:
    """Return the lower bound of the 5 cm DBH class for a diameter."""
    if not np.isfinite(dbh_cm):
        raise ValueError("DBH must be finite")
    return min(DBH_CLASS_MAX, max(0, int(dbh_cm // DBH_CLASS_WIDTH) * DBH_CLASS_WIDTH))


def collapse_tree_ids(trees: pd.DataFrame) -> pd.DataFrame:
    """Collapse FVS's split records to one row per AU, treatment, year, and tree id.

    FVS can emit several rows with the same ``TreeId`` after a treatment. The
    rows are records of the same tree, not independent trees; sum their TPH and
    volume and use the TPH-weighted DBH. This is the key that makes a
    tree-level transition possible.
    """
    frame = trees.copy()
    frame["volume_m3"] = frame["MCuM"].fillna(0.0).astype(float)
    frame["weighted_dbh"] = frame["DBH"].astype(float) * frame["TPH"].astype(float)
    grouped = (
        frame.groupby(["au", "treatment", "Year", "TreeId"], observed=True)
        .agg(
            tph=("TPH", "sum"),
            volume_m3=("volume_m3", "sum"),
            weighted_dbh=("weighted_dbh", "sum"),
        )
        .reset_index()
    )
    grouped["DBH"] = grouped["weighted_dbh"] / grouped["tph"].where(grouped["tph"] > 0.0, 1.0)
    return grouped.rename(columns={"volume_m3": "MCuM", "tph": "TPH"})


def distribution_frame(trees: pd.DataFrame) -> pd.DataFrame:
    """Aggregate tree lists into DBH-class distributions.

    Parameters
    ----------
    trees : pandas.DataFrame
        Tree-list rows with ``au``, ``treatment``, ``Year``, ``DBH``, ``TPH``
        and ``MCuM``.

    Returns
    -------
    pandas.DataFrame
        One row per AU, treatment, year, and DBH class.
    """
    frame = collapse_tree_ids(trees)
    frame["dbh_class_cm"] = frame["DBH"].map(dbh_class)
    frame["volume_m3"] = frame["MCuM"].fillna(0.0).astype(float)
    grouped = (
        frame.groupby(
            ["au", "treatment", "Year", "dbh_class_cm"],
            observed=True,
            dropna=False,
        )
        .agg(
            tph=("TPH", "sum"),
            volume_m3=("volume_m3", "sum"),
            tree_records=("TreeId", "size"),
        )
        .reset_index()
    )
    return grouped.sort_values(["au", "treatment", "Year", "dbh_class_cm"])


def _cut_ids(cuts: pd.DataFrame, *, au: int, treatment: str, year: int) -> set[str]:
    """Return the tree ids cut for an AU/treatment/year interval."""
    if cuts.empty:
        return set()
    mask = (
        (cuts["au"] == au)
        & (cuts["treatment"] == treatment)
        & (cuts["Year"] >= year)
        & (cuts["Year"] < year + 10)
    )
    return {str(value) for value in cuts.loc[mask, "TreeId"].dropna().tolist()}


def transition_frame(
    trees: pd.DataFrame,
    cuts: pd.DataFrame,
) -> pd.DataFrame:
    """Build ten-year DBH-class transitions from tree lists and cut lists.

    Parameters
    ----------
    trees : pandas.DataFrame
        Tree-list rows with ``au``, ``treatment``, ``Year``, ``TreeId``,
        ``DBH``, ``TPH`` and ``MCuM``.
    cuts : pandas.DataFrame
        Cut-list rows with ``au``, ``treatment``, ``Year`` and ``TreeId``.

    Returns
    -------
    pandas.DataFrame
        One row per AU, treatment, interval, source DBH class, destination
        DBH class, and fate.
    """
    work = collapse_tree_ids(trees)
    work["volume_m3"] = work["MCuM"].fillna(0.0).astype(float)
    rows: list[pd.DataFrame] = []
    for (au, treatment), group in work.groupby(["au", "treatment"], observed=True):
        years = sorted(int(year) for year in group["Year"].unique())
        for year in years:
            if year + 10 not in years:
                continue
            source = group[group["Year"] == year].copy()
            target = group[group["Year"] == year + 10].copy()
            target_lookup = target.set_index("TreeId")
            cut_ids = _cut_ids(
                cuts,
                au=int(au),
                treatment=str(treatment),
                year=year,
            )
            records: list[dict[str, object]] = []
            for row in source.itertuples(index=False):
                tree_id = str(row.TreeId)
                from_tph = float(row.TPH)
                from_class = int(dbh_class(float(row.DBH)))
                base = {
                    "au": int(au),
                    "treatment": str(treatment),
                    "year_from": year,
                    "year_to": year + 10,
                    "TreeId": tree_id,
                    "dbh_from_cm": from_class,
                }

                parts: list[tuple[str, int | None, float]] = []
                if tree_id in target_lookup.index:
                    target_row = target_lookup.loc[tree_id]
                    to_tph = float(target_row["TPH"])
                    live_tph = min(from_tph, to_tph)
                    removed_tph = max(0.0, from_tph - to_tph)
                    parts.append(("live", int(dbh_class(float(target_row["DBH"]))), live_tph))
                    parts.append(
                        (
                            "harvest" if cut_ids else "mortality",
                            None,
                            removed_tph,
                        )
                    )
                else:
                    parts.append(("harvest" if cut_ids else "mortality", None, from_tph))
                for fate, to_class, part_tph in parts:
                    if part_tph <= 1e-12:
                        continue
                    records.append(
                        {
                            **base,
                            "dbh_to_cm": to_class,
                            "fate": fate,
                            "tph": part_tph,
                            "volume_m3": float(row.volume_m3)
                            * (part_tph / from_tph if from_tph else 0.0),
                        }
                    )
            frame = pd.DataFrame(records)
            if frame.empty:
                continue
            rows.append(
                frame.groupby(
                    [
                        "au",
                        "treatment",
                        "year_from",
                        "year_to",
                        "dbh_from_cm",
                        "dbh_to_cm",
                        "fate",
                    ],
                    observed=True,
                    dropna=False,
                )
                .agg(tph=("tph", "sum"), volume_m3=("volume_m3", "sum"))
                .reset_index()
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "au",
                "treatment",
                "year_from",
                "year_to",
                "dbh_from_cm",
                "dbh_to_cm",
                "fate",
                "tph",
                "volume_m3",
            ]
        )
    return pd.concat(rows, ignore_index=True).sort_values(
        ["au", "treatment", "year_from", "dbh_from_cm", "fate", "dbh_to_cm"]
    )


def main() -> None:
    """Read the pilot tree lists and write distributions and transitions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilot-dir",
        type=Path,
        default=Path("data/fvsbc/gl_pilot"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/fvsbc/gl_pilot"),
    )
    args = parser.parse_args()
    trees = pd.read_parquet(args.pilot_dir / "tree_trajectories.parquet")
    cuts = pd.read_parquet(args.pilot_dir / "cut_list.parquet")
    distribution = distribution_frame(trees)
    transitions = transition_frame(trees, cuts)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    distribution.to_csv(args.out_dir / "dbh_distribution.csv", index=False)
    transitions.to_parquet(args.out_dir / "transitions.parquet", index=False)
    payload = {
        "distribution_rows": len(distribution),
        "transition_rows": len(transitions),
        "aus": sorted(int(value) for value in transitions["au"].unique()),
        "treatments": sorted(str(value) for value in transitions["treatment"].unique()),
        "years": sorted(int(value) for value in transitions["year_from"].unique()),
        "fates": {
            str(key): int(value) for key, value in transitions.groupby("fate").size().items()
        },
    }
    (args.out_dir / "transitions_summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

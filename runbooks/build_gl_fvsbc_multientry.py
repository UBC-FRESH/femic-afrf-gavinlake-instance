#!/usr/bin/env python3
"""Run a second FVS-BC entry from the post-treatment tree list.

The first entry is the existing FVS-BC `ct60` or `selection80` run. Its year-10
tree list is the post-treatment state. This script feeds that tree list back into
FVS-BC for a second entry and records the second-entry growth and harvest.

This is a chain of two FVS cases, not a re-simulation of the original stand.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from fresh_fvsbc.keywords import Keyword
    from fresh_fvsbc.run import RunResult


def _require_fvsbc() -> tuple[object, object, object]:
    """Import the FVS-BC API only when a run is requested."""
    from fresh_fvsbc.keywords import Keyword
    from fresh_fvsbc.outputs import read_table
    from fresh_fvsbc.run import run_case

    return Keyword, read_table, run_case


def _tree_records(
    tree_list: pd.DataFrame,
    *,
    age: float,
) -> tuple[list[dict[str, float | int | str]], float]:
    """Convert one FVS tree list into records and return the initial BA."""
    grouped = (
        tree_list.groupby("TreeId", observed=True)
        .agg(
            tph=("TPH", "sum"),
            dbh=("DBH", "mean"),
            height=("Ht", "mean"),
            species=("SpeciesFVS", "first"),
            crown=("PctCr", "mean"),
        )
        .reset_index()
    )
    records: list[dict[str, float | int | str]] = []
    total_ba = 0.0
    for index, row in enumerate(grouped.itertuples(index=False), start=1):
        tph = float(row.tph)
        if tph <= 0.0:
            continue
        diameter = float(row.dbh)
        total_ba += math.pi * (diameter / 200.0) ** 2 * tph
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": round(tph),
                "tree_history": 0,
                "species": str(row.species),
                "diam": diameter,
                "dg_incr": 0.0,
                "live_ht": float(row.height),
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": min(9, max(1, round(float(row.crown) / 10.0))),
                "damage1": 0,
                "severity1": 0,
                "damage2": 0,
                "severity2": 0,
                "damage3": 0,
                "severity3": 0,
                "tree_val": 0,
                "tree_rx": 0,
                "plot_slope": 15,
                "plot_aspect": 0,
                "plot_habitat": 0,
                "plot_topo_pos": 0,
                "plot_site_prep": 0,
                "tree_age": float(age),
            }
        )
    return records, total_ba


def _keywords(
    *,
    au: int,
    treatment: str,
    initial_ba: float,
    site_species: str,
    site_index: float,
) -> tuple[Keyword, ...]:
    """Return the second-entry keyword set."""
    keyword_cls, _, _ = _require_fvsbc()
    target = max(0.0, 0.6 * initial_ba if treatment == "ct60" else 0.8 * initial_ba)
    return (
        keyword_cls(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "Summary", "TREELIDB", "CUTLIDB", "ComputDB"),
        ),
        keyword_cls("STDIDENT", (f"AU{au} second {treatment}",)),
        keyword_cls("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        keyword_cls("MANAGED", ("0", "1")),
        keyword_cls("SITECODE", (site_species, f"{site_index:.0f}")),
        keyword_cls("INVYEAR", ("0",)),
        keyword_cls("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        keyword_cls("NUMCYCLE", ("10",)),
        keyword_cls("RANNSEED", ("1",)),
        keyword_cls("TREELIST", ("0",)),
        keyword_cls("CUTLIST", ("0",)),
        keyword_cls("THINBBA", ("1", f"{target:.2f}", "0.95", "0.0", "999.0", "0", "999")),
        keyword_cls("ECHOSUM"),
        keyword_cls("PROCESS"),
        keyword_cls("STOP"),
    )


def _run_one(
    *,
    au: int,
    treatment: str,
    tree_list: pd.DataFrame,
    age: float,
    site_species: str,
    site_index: float,
    run_dir: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Run a second entry and return its summary and metadata."""
    _, read_table, run_case = _require_fvsbc()
    records, initial_ba = _tree_records(tree_list, age=age)
    if not records:
        raise ValueError(f"AU {au} {treatment}: no live post-treatment records")
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    keywords = _keywords(
        au=au,
        treatment=treatment,
        initial_ba=initial_ba,
        site_species=site_species,
        site_index=site_index,
    )
    result: RunResult = run_case(records, keywords, directory=run_dir)
    summary = read_table(result.database, "FVS_Summary_Metric")
    if summary is None:
        raise RuntimeError(f"missing summary for AU {au} {treatment}")
    summary = summary.copy()
    summary["au"] = au
    summary["entry"] = 2
    summary["treatment"] = treatment
    summary["initial_ba_m2_ha"] = initial_ba
    metadata: dict[str, object] = {
        "au": au,
        "treatment": treatment,
        "tree_count": len(records),
        "initial_ba_m2_ha": initial_ba,
        "case_id": result.provenance.case_id,
        "warnings": result.warnings.to_dict("records"),
    }
    return summary, metadata


def main() -> None:
    """Run second-entry FVS-BC cases for the pilot AUs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trajectories",
        type=Path,
        default=Path("data/fvsbc/gl_all/tree_trajectories.parquet"),
    )
    parser.add_argument(
        "--runs",
        type=Path,
        default=Path("data/fvsbc/gl_all/runs.csv"),
    )
    parser.add_argument(
        "--cuts",
        type=Path,
        default=Path("data/fvsbc/gl_all/cut_list.parquet"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/fvsbc/gl_multientry"),
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=Path("ws4/runtime/fvsbc_multientry/runs"),
    )
    parser.add_argument("--aus", default="2,302,352,312,802,502")
    parser.add_argument("--treatments", default="ct60,selection80")
    args = parser.parse_args()
    aus = tuple(int(value) for value in args.aus.split(",") if value.strip())
    treatments = tuple(value.strip() for value in args.treatments.split(",") if value.strip())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runs_dir.mkdir(parents=True, exist_ok=True)

    trajectories = pd.read_parquet(
        args.trajectories,
        columns=["au", "treatment", "Year", "TreeId", "TPH", "DBH", "Ht", "SpeciesFVS", "PctCr"],
    )
    runs = pd.read_csv(args.runs).drop_duplicates(["au", "treatment"])
    cuts = pd.read_parquet(args.cuts)
    summaries: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, object]] = []
    for au in aus:
        for treatment in treatments:
            source = trajectories[
                (trajectories["au"] == au)
                & (trajectories["treatment"] == treatment)
                & (trajectories["Year"] == 10)
            ]
            if source.empty:
                print(f"skip AU {au} {treatment}: no year-10 tree list", flush=True)
                continue
            cut_ids = set(
                cuts[(cuts["au"] == au) & (cuts["treatment"] == treatment) & (cuts["Year"] == 0)][
                    "TreeId"
                ].astype(str)
            )
            source = source[~source["TreeId"].astype(str).isin(cut_ids)]
            run_row = runs[(runs["au"] == au) & (runs["treatment"] == treatment)].iloc[0]
            age = float(run_row["tree_age"]) + 10.0
            site_species = str(run_row["site_species"])
            site_index = float(run_row["site_index"])
            print(f"AU {au} second {treatment}", flush=True)
            summary, metadata = _run_one(
                au=au,
                treatment=treatment,
                tree_list=source,
                age=age,
                site_species=site_species,
                site_index=site_index,
                run_dir=args.runs_dir / f"au_{au:04d}" / treatment,
            )
            summaries.append(summary)
            metadata_rows.append(metadata)
    curves = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    metadata = pd.DataFrame(metadata_rows)
    curves.to_csv(args.out_dir / "second_entry_curves.csv", index=False)
    metadata.to_csv(args.out_dir / "second_entry_runs.csv", index=False)
    summary = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "aus": list(aus),
        "treatments": list(treatments),
        "runs": len(metadata),
        "curves": len(curves),
        "caveats": [
            "Second entry starts from the FVS year-10 post-treatment tree list.",
            "The chain is two FVS cases; it is not a continuous single projection.",
            "The same AU site code is retained; the post-treatment state is sampled.",
            "No regeneration, ingress, planting, fire, or climate extension is modelled.",
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

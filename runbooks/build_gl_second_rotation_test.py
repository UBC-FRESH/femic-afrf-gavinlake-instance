#!/usr/bin/env python3
"""Test whether the first-rotation AAC survives a second rotation.

The first-rotation schedule harvests each block once. This script adds the
standing volume of the planted regeneration curve at age 80 and assigns that
second harvest to the period 80 years after the first entry.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

SECOND_ROTATION_AGE = 80
PERIOD_YEARS = 10


def au_by_block(blocks: pd.DataFrame, tracks: pd.DataFrame) -> pd.Series:
    """Return the AU for each block."""
    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    merged = blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
    return merged.dropna(subset=["au"]).groupby("block_id")["au"].first()


def second_rotation_table(
    schedule: pd.DataFrame,
    *,
    area_by_block: pd.Series,
    au_by_block: pd.Series,
    regen: pd.DataFrame,
) -> pd.DataFrame:
    """Return second-rotation volume by block and period."""
    frame = schedule.copy()
    frame["au"] = frame["block_id"].map(au_by_block)
    frame["area_ha"] = frame["block_id"].map(area_by_block)
    age80 = regen[regen["Year"] == SECOND_ROTATION_AGE].set_index("au")["MCuM"].astype(float)
    frame["second_rotation_m3"] = frame["area_ha"] * frame["au"].map(age80)
    frame["second_period"] = (frame["offset"] + SECOND_ROTATION_AGE) // PERIOD_YEARS * PERIOD_YEARS
    return frame


def main() -> None:
    """Write the second-rotation test table and summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schedule",
        type=Path,
        default=Path("data/fvsbc/gl_all/ws4_cohort_graph/schedules/evenflow_ltsy.csv"),
    )
    parser.add_argument(
        "--fragments",
        type=Path,
        default=Path("data/fvsbc/gl_all/ws4_cohort_graph/fragments.parquet"),
    )
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("ws4/runtime/legacy_matrix/blocks.parquet"),
    )
    parser.add_argument(
        "--tracks",
        type=Path,
        default=Path("ws4/runtime/legacy_matrix/tracks.parquet"),
    )
    parser.add_argument(
        "--regen",
        type=Path,
        default=Path("data/fvsbc/gl_regen/regen_curves.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/fvsbc/gl_second_rotation"),
    )
    args = parser.parse_args()
    schedule = pd.read_csv(args.schedule)
    fragments = pd.read_parquet(args.fragments)
    blocks = pd.read_parquet(args.blocks)
    tracks = pd.read_parquet(args.tracks)
    regen = pd.read_csv(args.regen)
    area = fragments.groupby("block_id")["area_ha"].sum()
    table = second_rotation_table(
        schedule,
        area_by_block=area,
        au_by_block=au_by_block(blocks, tracks),
        regen=regen,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out_dir / "second_rotation.csv", index=False)
    periods = table.groupby("second_period")["second_rotation_m3"].sum().reset_index()
    periods.to_csv(args.out_dir / "second_rotation_by_period.csv", index=False)
    total = float(table["second_rotation_m3"].sum())
    payload = {
        "blocks": len(table),
        "area_ha": float(table["area_ha"].sum()),
        "second_rotation_total_m3": total,
        "second_rotation_mean_per_decade_m3": total / 10.0,
        "first_rotation_target_m3_per_decade": 185000.0,
        "first_rotation_actual_m3_per_decade": float(schedule["estimated_volume_m3"].sum() / 10.0),
        "second_rotation_holds_target": bool(total / 10.0 >= 185000.0),
        "caveat": (
            "Second rotation is the planted FVS curve at age 80, applied only to "
            "blocks harvested in the first rotation. It is not a scheduled "
            "second harvest or a natural-regeneration projection."
        ),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a 200-year first-plus-second-rotation schedule.

Each block gets one first-rotation clearcut and one second-rotation clearcut 80
years later. The schedule is a greedy balance of the twenty ten-year periods,
not a formal optimizer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PERIOD_YEARS = 10
SECOND_AGE = 80


def _curve_value(curve: pd.DataFrame, x: float) -> float:
    """Interpolate one cut curve at x."""
    if curve.empty:
        return 0.0
    ordered = curve.sort_values("x")
    xs = ordered["x"].to_numpy(dtype=float)
    ys = ordered["y"].to_numpy(dtype=float)
    if x < xs.min() or x > xs.max():
        return 0.0
    return float(np.interp(x, xs, ys))


def first_rotation_volumes(
    fragments: pd.DataFrame,
    products: pd.DataFrame,
    curves: pd.DataFrame,
) -> pd.DataFrame:
    """Return block x first-entry-offset volume."""
    cut = products[
        (products["label"] == "product.harvest.total")
        & products["treatment"].str.startswith("CLEARCUT_E")
    ]
    by_track = {
        (int(row.track_id), str(row.treatment)): int(row.curve_id)
        for row in cut.itertuples(index=False)
    }
    curve_lookup = {
        int(row.curve_id): curves[curves["curve_id"] == int(row.curve_id)]
        for row in cut.drop_duplicates("curve_id").itertuples(index=False)
    }
    offsets = sorted(
        int(str(label).removeprefix("CLEARCUT_E")) for label in cut["treatment"].unique()
    )
    rows: list[dict[str, float | int]] = []
    for fragment in fragments.itertuples(index=False):
        track = int(fragment.track_id)
        age_bin = int(fragment.age) // PERIOD_YEARS * PERIOD_YEARS
        area = float(fragment.area_ha)
        for offset in offsets:
            curve_id = by_track.get((track, f"CLEARCUT_E{offset}"))
            if curve_id is None:
                continue
            value = _curve_value(curve_lookup[curve_id], age_bin + offset)
            if value > 0.0:
                rows.append(
                    {
                        "block_id": int(fragment.block_id),
                        "offset": offset,
                        "volume_m3": area * value,
                    }
                )
    return pd.DataFrame(rows).groupby(["block_id", "offset"], as_index=False)["volume_m3"].sum()


def second_rotation_volumes(
    *,
    fragments: pd.DataFrame,
    blocks: pd.DataFrame,
    tracks: pd.DataFrame,
    regen: pd.DataFrame,
) -> pd.Series:
    """Return one second-rotation volume per block."""
    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    block_au = (
        blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
        .dropna(subset=["au"])
        .set_index("block_id")["au"]
    )
    area = fragments.groupby("block_id")["area_ha"].sum()
    age80 = regen[regen["Year"] == SECOND_AGE].set_index("au")["MCuM"].astype(float)
    au = area.index.map(block_au)
    return pd.Series(
        area.to_numpy(dtype=float) * np.asarray(age80.reindex(au), dtype=float),
        index=area.index,
        dtype=float,
    )


def greedy_200_year(
    first: pd.DataFrame,
    second: pd.Series,
) -> pd.DataFrame:
    """Assign one first and one second cut per block across twenty periods."""
    pivot = first.pivot(index="block_id", columns="offset", values="volume_m3").fillna(0.0)
    offsets = [int(value) for value in pivot.columns]
    totals = [0.0] * 20
    rows: list[dict[str, float | int | str]] = []
    order = pivot.assign(max_volume=pivot.max(axis=1)).sort_values("max_volume", ascending=False)
    for block_id, row in order.iterrows():
        second_volume = float(second.get(block_id, 0.0))
        best_offset = offsets[0]
        best_score = float("inf")
        for offset in offsets:
            first_volume = float(row.get(offset, 0.0))
            if first_volume <= 0.0:
                continue
            first_period = offset // PERIOD_YEARS
            second_period = first_period + SECOND_AGE // PERIOD_YEARS
            score = max(
                totals[first_period] + first_volume,
                totals[second_period] + second_volume,
            )
            if score < best_score:
                best_score = score
                best_offset = offset
        first_volume = float(row.get(best_offset, 0.0))
        first_period = best_offset // PERIOD_YEARS
        second_period = first_period + SECOND_AGE // PERIOD_YEARS
        totals[first_period] += first_volume
        totals[second_period] += second_volume
        rows.append(
            {
                "block_id": int(block_id),
                "first_offset": best_offset,
                "first_period": first_period * PERIOD_YEARS,
                "first_volume_m3": first_volume,
                "second_period": second_period * PERIOD_YEARS,
                "second_volume_m3": second_volume,
            }
        )
    table = pd.DataFrame(rows)
    return table


def main() -> None:
    """Write the 200-year schedule and period totals."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/fvsbc/gl_all/ws4_cohort_graph"))
    parser.add_argument(
        "--blocks", type=Path, default=Path("ws4/runtime/legacy_matrix/blocks.parquet")
    )
    parser.add_argument(
        "--tracks", type=Path, default=Path("ws4/runtime/legacy_matrix/tracks.parquet")
    )
    parser.add_argument("--regen", type=Path, default=Path("data/fvsbc/gl_regen/regen_curves.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/fvsbc/gl_second_rotation"))
    args = parser.parse_args()
    fragments = pd.read_parquet(args.dataset / "fragments.parquet")
    products = pd.read_parquet(args.dataset / "products.parquet")
    curves = pd.read_parquet(args.dataset / "curves.parquet")
    blocks = pd.read_parquet(args.blocks)
    tracks = pd.read_parquet(args.tracks)
    regen = pd.read_csv(args.regen)
    first = first_rotation_volumes(fragments, products, curves)
    second = second_rotation_volumes(
        fragments=fragments,
        blocks=blocks,
        tracks=tracks,
        regen=regen,
    )
    table = greedy_200_year(first, second)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out_dir / "schedule_200_year.csv", index=False)
    periods = []
    for period in range(0, 200, PERIOD_YEARS):
        first_v = table.loc[table["first_period"] == period, "first_volume_m3"].sum()
        second_v = table.loc[table["second_period"] == period, "second_volume_m3"].sum()
        periods.append(
            {
                "period_year": period,
                "first_rotation_m3": float(first_v),
                "second_rotation_m3": float(second_v),
                "total_m3": float(first_v + second_v),
            }
        )
    period_frame = pd.DataFrame(periods)
    period_frame.to_csv(args.out_dir / "schedule_200_year_by_period.csv", index=False)
    totals = period_frame["total_m3"]
    payload = {
        "blocks": len(table),
        "periods": 20,
        "mean_m3_per_decade": float(totals.mean()),
        "min_m3_per_decade": float(totals.min()),
        "max_m3_per_decade": float(totals.max()),
        "first_rotation_total_m3": float(table["first_volume_m3"].sum()),
        "second_rotation_total_m3": float(table["second_volume_m3"].sum()),
        "caveat": (
            "Greedy 200-year assignment, not an optimizer. The second rotation is "
            "the planted FVS curve at age 80; no natural ingress or fire."
        ),
    }
    (args.out_dir / "schedule_200_year.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

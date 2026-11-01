#!/usr/bin/env python3
"""Build a greedy ten-period even-flow schedule on the cohort graph.

Every block gets one `CT60` entry at a ten-year offset. The block is assigned to
the period whose current plus candidate harvest is smallest. The schedule is a
screening heuristic, not an optimal solution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PERIOD_YEARS = 10


def _curve_value(curve: pd.DataFrame, x: float) -> float:
    """Interpolate one cut curve at an entry age."""
    if curve.empty:
        return 0.0
    ordered = curve.sort_values("x")
    xs = ordered["x"].to_numpy(dtype=float)
    ys = ordered["y"].to_numpy(dtype=float)
    if x < xs.min() or x > xs.max():
        return 0.0
    return float(np.interp(x, xs, ys))


def block_volumes(
    fragments: pd.DataFrame,
    products: pd.DataFrame,
    curves: pd.DataFrame,
) -> pd.DataFrame:
    """Return one block x offset harvest-volume table."""
    cut_products = products[products["label"] == "product.harvest.total"].copy()
    cut_products = cut_products[cut_products["treatment"].str.startswith("CT60_E")]
    curve_lookup = {
        int(row.curve_id): curves[curves["curve_id"] == int(row.curve_id)]
        for row in cut_products.drop_duplicates("curve_id").itertuples(index=False)
    }
    by_track: dict[tuple[int, str], int] = {
        (int(row.track_id), str(row.treatment)): int(row.curve_id)
        for row in cut_products.itertuples(index=False)
    }
    offsets = sorted(
        int(str(label).removeprefix("CT60_E")) for label in cut_products["treatment"].unique()
    )
    rows: list[dict[str, float | int]] = []
    for fragment in fragments.itertuples(index=False):
        track = int(fragment.track_id)
        age = int(fragment.age)
        area = float(fragment.area_ha)
        for offset in offsets:
            curve_id = by_track.get((track, f"CT60_E{offset}"))
            if curve_id is None:
                continue
            value = _curve_value(
                curve_lookup[curve_id], (age // PERIOD_YEARS) * PERIOD_YEARS + offset
            )
            if value > 0.0:
                rows.append(
                    {
                        "block_id": int(fragment.block_id),
                        "offset": offset,
                        "volume_m3": area * value,
                    }
                )
    table = pd.DataFrame(rows)
    return table.groupby(["block_id", "offset"], as_index=False)["volume_m3"].sum()


def greedy_schedule(volumes: pd.DataFrame) -> pd.DataFrame:
    """Assign each block to the least-loaded period."""
    offsets = sorted(int(value) for value in volumes["offset"].unique())
    pivot = volumes.pivot(index="block_id", columns="offset", values="volume_m3").fillna(0.0)
    totals = dict.fromkeys(offsets, 0.0)
    rows: list[dict[str, float | int]] = []
    order = pivot.assign(max_volume=pivot.max(axis=1)).sort_values("max_volume", ascending=False)
    for block_id, row in order.iterrows():
        best = min(
            offsets,
            key=lambda offset: totals[offset] + float(row.get(offset, 0.0)),
        )
        volume = float(row.get(best, 0.0))
        totals[best] += volume
        rows.append(
            {
                "block_id": int(block_id),
                "treatment": f"CT60_E{best}",
                "offset": best,
                "estimated_volume_m3": volume,
            }
        )
    return pd.DataFrame(rows).sort_values(["offset", "block_id"])


def main() -> None:
    """Write the schedule and its estimated period totals."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("ws4/runtime/fvsbc_cohort_graph"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/fvsbc/gl_all/ws4_cohort_graph/schedules/evenflow.csv"),
    )
    args = parser.parse_args()
    fragments = pd.read_parquet(args.dataset / "fragments.parquet")
    products = pd.read_parquet(args.dataset / "products.parquet")
    curves = pd.read_parquet(args.dataset / "curves.parquet")
    volumes = block_volumes(fragments, products, curves)
    schedule = greedy_schedule(volumes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    schedule.to_csv(args.out, index=False)
    totals = schedule.groupby("offset")["estimated_volume_m3"].sum().reset_index()
    payload = {
        "rows": len(schedule),
        "period_years": PERIOD_YEARS,
        "estimated_period_volume_m3": {
            str(int(row.offset)): round(float(row.estimated_volume_m3), 1)
            for row in totals.itertuples(index=False)
        },
        "caveat": (
            "Greedy assignment of one CT60 entry per block; estimated from cut "
            "curves, not an optimizer solution."
        ),
    }
    args.out.with_suffix(".json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare the FVS-BC AU curves with the legacy clearcut yield matrix.

The legacy curve is an 80-year clearcut rotation, not a partial-harvest state.
This script therefore reports a screening comparison:

- legacy yield at the current VRI age versus the FVS initial volume; and
- legacy yield at current age + 100 versus the untreated FVS volume at year 100.

It does not treat the legacy curve as a validated target for the FVS runs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

#: The legacy product label that carries total managed yield.
LEGACY_LABEL: str = "product.yield.managed.total"


def interpolate_curve(
    curve: pd.DataFrame,
    *,
    age: float,
) -> float:
    """Interpolate a legacy yield curve, or return NaN outside its domain."""
    if curve.empty:
        return float("nan")
    ordered = curve.sort_values("x")
    x = ordered["x"].to_numpy(dtype=float)
    y = ordered["y"].to_numpy(dtype=float)
    if age < x.min() or age > x.max():
        return float("nan")
    return float(np.interp(age, x, y))


def main() -> None:
    """Write the AU-level legacy comparison table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fvs-dir", type=Path, default=Path("data/fvsbc/gl_all"))
    parser.add_argument(
        "--legacy-dir",
        type=Path,
        default=Path("ws4/runtime/legacy_matrix"),
    )
    args = parser.parse_args()

    runs = pd.read_csv(args.fvs_dir / "runs.csv").drop_duplicates(["au", "treatment"])
    curves = pd.read_csv(args.fvs_dir / "curves.csv")
    blocks = pd.read_parquet(args.legacy_dir / "blocks.parquet")
    tracks = pd.read_parquet(args.legacy_dir / "tracks.parquet")
    products = pd.read_parquet(args.legacy_dir / "products.parquet")
    legacy_curves = pd.read_parquet(args.legacy_dir / "curves.parquet")

    rows: list[dict[str, float | int]] = []
    for au in sorted(int(value) for value in runs["au"].unique()):
        run = runs[(runs["au"] == au) & (runs["treatment"] == "untreated")]
        if run.empty:
            continue
        age = float(run.iloc[0]["tree_age"])
        fvs_init = float(
            curves[
                (curves["au"] == au) & (curves["treatment"] == "untreated") & (curves["Year"] == 0)
            ]["MCuM"].iloc[0]
        )
        fvs_final = float(
            curves[
                (curves["au"] == au)
                & (curves["treatment"] == "untreated")
                & (curves["Year"] == 100)
            ]["MCuM"].iloc[0]
        )
        parsed = tracks.copy()
        parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
        selected_tracks = blocks.merge(parsed[["track_id", "au"]], on="track_id")
        selected_tracks = selected_tracks[selected_tracks["au"] == au]
        track_area = selected_tracks.groupby("track_id")["area_ha"].sum()
        product = products[products["label"] == LEGACY_LABEL][["track_id", "curve_id"]]
        merged = track_area.rename("area_ha").reset_index().merge(product, on="track_id")
        values_current: list[float] = []
        weights_current: list[float] = []
        values_future: list[float] = []
        weights_future: list[float] = []
        for record in merged.itertuples(index=False):
            curve = legacy_curves[legacy_curves["curve_id"] == int(record.curve_id)]
            current = interpolate_curve(curve, age=age)
            future = interpolate_curve(curve, age=age + 100.0)
            if np.isfinite(current):
                values_current.append(current)
                weights_current.append(float(record.area_ha))
            if np.isfinite(future):
                values_future.append(future)
                weights_future.append(float(record.area_ha))
        legacy_current = (
            float(np.average(values_current, weights=weights_current))
            if weights_current
            else float("nan")
        )
        legacy_future = (
            float(np.average(values_future, weights=weights_future))
            if weights_future
            else float("nan")
        )
        rows.append(
            {
                "au": au,
                "age": age,
                "legacy_tracks": len(merged),
                "legacy_current_m3_ha": legacy_current,
                "fvs_initial_m3_ha": fvs_init,
                "initial_difference_pct": (
                    100.0 * (fvs_init - legacy_current) / legacy_current
                    if np.isfinite(legacy_current) and legacy_current
                    else float("nan")
                ),
                "legacy_age_plus_100_m3_ha": legacy_future,
                "fvs_untreated_year_100_m3_ha": fvs_final,
                "future_difference_pct": (
                    100.0 * (fvs_final - legacy_future) / legacy_future
                    if np.isfinite(legacy_future) and legacy_future
                    else float("nan")
                ),
            }
        )
    comparison = pd.DataFrame(rows).sort_values("au")
    comparison.to_csv(args.fvs_dir / "legacy_comparison.csv", index=False)
    payload = {
        "rows": len(comparison),
        "finite_initial": int(comparison["legacy_current_m3_ha"].notna().sum()),
        "finite_future": int(comparison["legacy_age_plus_100_m3_ha"].notna().sum()),
        "median_initial_difference_pct": float(comparison["initial_difference_pct"].median()),
        "median_future_difference_pct": float(comparison["future_difference_pct"].median()),
        "caveat": (
            "The legacy curve is an 80-year clearcut rotation; the FVS runs are "
            "partial-harvest states. This is a screening comparison, not a parity test."
        ),
    }
    (args.fvs_dir / "legacy_comparison_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a 2025 VRI starting-age and species layer for Gavin Lake.

The legacy model starts from `AGE_2019`. This runbook joins each legacy fragment
to the 2025 VRI, advances the VRI projected age to 2025, and records the
difference from the legacy age. It is a rebuild input, not an applied change to
the compiled legacy matrix.

Usage::

    python runbooks/build_gavin_vri_start.py \
      --out-dir data/inventory
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

START_YEAR = 2025


def main() -> None:
    """Write the 2025 VRI starting layer and summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fragments",
        type=Path,
        default=Path("data/legacy_gavinlake/spatial/fragments.shp"),
    )
    parser.add_argument(
        "--vri",
        type=Path,
        default=Path("data/inventory/vri_gavin_2025.gpkg"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/inventory"))
    args = parser.parse_args()

    fragments = gpd.read_file(args.fragments).to_crs(3005)
    vri = gpd.read_file(args.vri).to_crs(3005)
    vri["vri_age_2025"] = vri["PROJ_AGE_1"] + (START_YEAR - vri["REFERENCE_YEAR"])
    overlay = gpd.overlay(
        fragments[["RES_KEY", "BLOCK_ID", "BEC", "AGE_2019", "geometry"]],
        vri[
            [
                "vri_age_2025",
                "SPECIES_CD_1",
                "SPECIES_PCT_1",
                "SPECIES_CD_2",
                "SPECIES_PCT_2",
                "SPECIES_CD_3",
                "SPECIES_PCT_3",
                "geometry",
            ]
        ],
        how="intersection",
        keep_geom_type=True,
    )
    overlay["piece_area"] = overlay.geometry.area

    rows: list[dict[str, object]] = []
    for fragment_id, group in overlay.groupby("RES_KEY"):
        weights = group["piece_area"].to_numpy(dtype=float)
        ages = group["vri_age_2025"].to_numpy(dtype=float)
        age = float(np.average(ages, weights=weights)) if weights.sum() > 0 else np.nan
        shares: dict[str, float] = {}
        for index in (1, 2, 3):
            for code, pct, area in zip(
                group[f"SPECIES_CD_{index}"],
                group[f"SPECIES_PCT_{index}"],
                weights,
                strict=True,
            ):
                if pd.isna(code) or pd.isna(pct):
                    continue
                key = str(code).upper()
                shares[key] = shares.get(key, 0.0) + float(pct) * area / 100.0
        total = sum(shares.values()) or 1.0
        rows.append(
            {
                "RES_KEY": fragment_id,
                "vri_age_2025": age,
                "vri_area_ha": weights.sum() / 10_000.0,
                **{f"species_{key}": value / total for key, value in shares.items()},
            }
        )
    vri_start = pd.DataFrame(rows)
    out = fragments[["RES_KEY", "BLOCK_ID", "BEC", "AGE_2019", "geometry"]].merge(
        vri_start, on="RES_KEY", how="left"
    )
    out["legacy_age_2025"] = out["AGE_2019"] + (START_YEAR - 2019)
    out["vri_age_2025"] = out["vri_age_2025"].fillna(out["legacy_age_2025"]).clip(lower=0)
    out["age_delta_vri_minus_legacy"] = out["vri_age_2025"] - out["legacy_age_2025"]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out.drop(columns="geometry").to_csv(args.out_dir / "gavin_vri_2025_start.csv", index=False)
    out.to_file(args.out_dir / "gavin_vri_2025_start.gpkg", driver="GPKG")

    area = out["vri_area_ha"].fillna(0.0)
    summary = {
        "fragments": len(out),
        "fragments_with_vri": int(out["vri_area_ha"].notna().sum()),
        "area_ha": float(area.sum()),
        "vri_age_2025_area_weighted_mean": float((out["vri_age_2025"] * area).sum() / area.sum()),
        "legacy_age_2025_area_weighted_mean": float(
            (out["legacy_age_2025"] * area).sum() / area.sum()
        ),
        "age_delta_area_weighted_mean": float(
            (out["age_delta_vri_minus_legacy"] * area).sum() / area.sum()
        ),
        "fragments_delta_gt_20y": int((out["age_delta_vri_minus_legacy"].abs() > 20).sum()),
        "species_area_weighted": {
            column.removeprefix("species_"): float(
                (out[column].fillna(0.0) * area).sum() / area.sum()
            )
            for column in out.columns
            if column.startswith("species_")
        },
        "caveats": [
            "VRI ages are projected ages advanced to 2025 from REFERENCE_YEAR.",
            "The legacy model still uses AGE_2019 and the legacy tracks; this "
            "table is the rebuild input, not an applied dataset update.",
            "VRI age and legacy age differ materially for many fragments.",
        ],
    }
    (args.out_dir / "gavin_vri_2025_start_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(
        f"fragments={summary['fragments']} "
        f"vri_age={summary['vri_age_2025_area_weighted_mean']:.1f} "
        f"legacy_age={summary['legacy_age_2025_area_weighted_mean']:.1f}"
    )


if __name__ == "__main__":
    main()

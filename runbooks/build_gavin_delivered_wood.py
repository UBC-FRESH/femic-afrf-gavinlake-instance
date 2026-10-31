#!/usr/bin/env python3
"""Build a screening delivered-wood account layer for Gavin Lake.

The route run assigns each block's total harvested volume to a candidate mill.
This runbook then:

- estimates block species composition from the 2025 VRI;
- maps species to the BC interior market groups;
- applies the BC interior log-market species/sort mix;
- applies the published June-August 2026 average prices; and
- writes block, year, mill, species-group, and sort volumes and values.

This is a screening layer. The sort mix is a regional market-purchase mix, not
an AFRF grade distribution, and the prices are regional averages, not AFRF
sales.

Usage::

    python runbooks/build_gavin_delivered_wood.py \
      --route-run ws4/runtime/gavin_delivered_wood_screening \
      --out-dir data/delivered_wood/gavin
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

SPECIES_GROUPS = {
    "FDI": "Df-Larch",
    "FD": "Df-Larch",
    "PLI": "SPF",
    "PL": "SPF",
    "SX": "SPF",
    "BL": "Hem-Bal",
    "CW": "Cedar",
    "AT": "Deciduous",
}
GROUP_SORTS = {
    "SPF": ("Sawlog", "Peelers", "Pulpwood"),
    "Df-Larch": ("Sawlog", "Peelers", "Pulpwood"),
    "Hem-Bal": ("Sawlog", "Pulpwood"),
    "Cedar": ("Sawlog",),
    "Deciduous": ("Other",),
    "Other": ("Other",),
}


def _block_species(
    blocks: gpd.GeoDataFrame,
    vri: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Return area-weighted species-group shares by block."""
    overlay = gpd.overlay(
        blocks[["RES_KEY", "geometry"]],
        vri,
        how="intersection",
        keep_geom_type=True,
    )
    overlay["piece_area"] = overlay.geometry.area
    rows: list[dict[str, object]] = []
    for _, row in overlay.iterrows():
        block_id = int(row["RES_KEY"])
        piece_area = float(row["piece_area"])
        for index in range(1, 7):
            code = row.get(f"SPECIES_CD_{index}")
            pct = row.get(f"SPECIES_PCT_{index}")
            if pd.isna(code) or pd.isna(pct):
                continue
            group = SPECIES_GROUPS.get(str(code).upper(), "Other")
            rows.append(
                {
                    "block_id": block_id,
                    "species_group": group,
                    "area_weight": piece_area * float(pct) / 100.0,
                }
            )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("VRI overlay produced no species shares")
    grouped = frame.groupby(["block_id", "species_group"], as_index=False)["area_weight"].sum()
    totals = grouped.groupby("block_id")["area_weight"].transform("sum")
    grouped["species_share"] = grouped["area_weight"] / totals
    shares = grouped.pivot(
        index="block_id", columns="species_group", values="species_share"
    ).fillna(0.0)
    shares = shares.reindex(columns=sorted(GROUP_SORTS), fill_value=0.0)
    all_blocks = pd.DataFrame({"block_id": sorted(blocks["RES_KEY"].astype(int))})
    shares = all_blocks.merge(shares, on="block_id", how="left").fillna(0.0)
    # Blocks with no VRI attribution fall back to Douglas-fir.
    empty = shares[sorted(GROUP_SORTS)].sum(axis=1) <= 0.0
    shares.loc[empty, "Df-Larch"] = 1.0
    return shares


def _sort_mix(prices: pd.DataFrame) -> pd.DataFrame:
    """Return a species-group and sort mix from the interior market volumes."""
    market = prices[prices["row_type"] == "species_group"].copy()
    rows: list[dict[str, object]] = []
    for group in GROUP_SORTS:
        source_group = "Other" if group in {"Deciduous", "Other"} else group
        part = market[market["species_group"] == source_group]
        total = float(part["volume_m3"].sum())
        for sort in GROUP_SORTS[group]:
            source_sort = "Other" if group in {"Deciduous", "Other"} else sort
            volume = float(part.loc[part["sort"] == source_sort, "volume_m3"].sum())
            share = volume / total if total > 0.0 else 0.0
            if total <= 0.0:
                share = 1.0 / len(GROUP_SORTS[group])
            rows.append(
                {
                    "species_group": group,
                    "sort": sort,
                    "market_volume_m3": volume,
                    "sort_share": share,
                }
            )
    mix = pd.DataFrame(rows)
    mix["sort_share"] = mix.groupby("species_group")["sort_share"].transform(
        lambda values: values / values.sum()
    )
    return mix


def main() -> None:
    """Build the delivered-wood tables and summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--route-run",
        type=Path,
        default=Path("ws4/runtime/gavin_delivered_wood_screening"),
    )
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/legacy_gavinlake/spatial/fragments.shp"),
    )
    parser.add_argument(
        "--vri",
        type=Path,
        default=Path("data/inventory/vri_gavin_2025.gpkg"),
    )
    parser.add_argument(
        "--prices",
        type=Path,
        default=Path("data/log_prices/bc_interior_log_market_2026-08.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/delivered_wood/gavin"),
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    route_values = pd.read_csv(args.route_run / "route_values.csv")
    route_cost = pd.read_csv(args.route_run / "route_cost_report.csv")
    blocks = gpd.read_file(args.blocks).to_crs(3005)
    vri = gpd.read_file(args.vri).to_crs(3005)
    prices = pd.read_csv(args.prices)
    shares = _block_species(blocks, vri)
    mix = _sort_mix(prices)

    price_lookup = prices[prices["row_type"] == "species_group"].set_index(
        ["species_group", "sort"]
    )["price_cad_m3"]
    rows: list[dict[str, object]] = []
    for _, route in route_values.iterrows():
        block_id = int(route["block_id"])
        block_shares = shares[shares["block_id"] == block_id]
        if block_shares.empty:
            continue
        for _, share_row in block_shares.iterrows():
            for group in GROUP_SORTS:
                species_share = float(share_row.get(group, 0.0))
                if species_share <= 0.0:
                    continue
                group_mix = mix[mix["species_group"] == group]
                for _, mix_row in group_mix.iterrows():
                    sort = str(mix_row["sort"])
                    volume = float(route["volume"]) * species_share * float(mix_row["sort_share"])
                    price_key = (
                        ("Other", "Other") if group in {"Deciduous", "Other"} else (group, sort)
                    )
                    price = price_lookup.get(price_key, np.nan)
                    value = volume * float(price) if pd.notna(price) else np.nan
                    rows.append(
                        {
                            "offset": int(route["offset"]),
                            "block_id": block_id,
                            "destination": route["destination"],
                            "species_group": group,
                            "sort": sort,
                            "volume_m3": volume,
                            "price_cad_m3": price,
                            "value_cad": value,
                        }
                    )
    delivered = pd.DataFrame(rows)
    delivered.to_csv(args.out_dir / "delivered_wood_values.csv", index=False)

    by_year = (
        delivered.groupby(["offset", "destination", "species_group", "sort"], as_index=False)
        .agg(volume_m3=("volume_m3", "sum"), value_cad=("value_cad", "sum"))
        .sort_values(["offset", "destination", "species_group", "sort"])
    )
    by_year.to_csv(args.out_dir / "delivered_wood_by_year.csv", index=False)
    by_mill = (
        delivered.groupby(["destination", "species_group", "sort"], as_index=False)
        .agg(volume_m3=("volume_m3", "sum"), value_cad=("value_cad", "sum"))
        .sort_values(["destination", "species_group", "sort"])
    )
    by_mill.to_csv(args.out_dir / "delivered_wood_by_mill.csv", index=False)

    summary = {
        "route_run": str(args.route_run),
        "routed_volume_m3": float(delivered["volume_m3"].sum()),
        "value_cad": float(delivered["value_cad"].sum(skipna=True)),
        "unpriced_volume_m3": float(
            delivered.loc[delivered["price_cad_m3"].isna(), "volume_m3"].sum()
        ),
        "haul_cost_cad": float(route_cost["HAUL_EXPENSE"].sum()),
        "maintenance_cost_cad": float(route_cost["MAINTAIN_EXPENSE"].sum()),
        "build_cost_cad": float(route_cost["BUILD_EXPENSE"].sum()),
        "route_years": int(route_cost["YEAR"].max()),
        "blocks_routed": int(route_values["block_id"].nunique()),
        "mills": sorted(route_values["destination"].unique().tolist()),
        "sort_mix": mix.to_dict(orient="records"),
        "caveats": [
            "Species composition is area-weighted from the 2025 VRI for Gavin Lake.",
            "Sort shares are the regional BC interior market-purchase mix, "
            "not an AFRF grade distribution.",
            "Prices are June-August 2026 regional averages, not AFRF sales.",
            "Deciduous and residual species use the Other/Other price as a proxy.",
            "Haul, maintenance, and build costs come from the screening route run.",
            "This is a screening delivered-wood layer, not an operational or legal model.",
        ],
    }
    (args.out_dir / "delivered_wood_metadata.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"volume={summary['routed_volume_m3']:.0f} value={summary['value_cad']:.0f} "
        f"mills={len(summary['mills'])} blocks={summary['blocks_routed']}"
    )


if __name__ == "__main__":
    main()

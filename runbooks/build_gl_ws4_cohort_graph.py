#!/usr/bin/env python3
"""Build the entry-age cohort graph for even-flow scheduling.

The spatial graph has one treatment track per AU/bin. That cannot schedule a
treatment in a chosen decade, because a treatment carries a fixed new-age
offset. This builder creates a track for every treatment and entry offset
(0, 20, 40, 60, 80 years), so a schedule can choose the entry decade without
resetting the fragment to the wrong age.

This is a one-entry-per-fragment cohort graph. It is the basis for the
even-flow schedule; it is not a repeated-entry sequence.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import geopandas as gpd
import pandas as pd
from ws4.model.schema import MANIFEST_NAME, SCHEMA_VERSION, TABLES_BY_NAME, coerce_to_schema
from ws4.model.types import CanonicalDatasetManifest

TREATMENT_LABELS: dict[str, str] = {
    "ct60": "CT60",
    "fuel50": "FUEL50",
    "selection80": "SELECTION80",
    "shelterwood40": "SHELTERWOOD40",
    "vr20": "VR20",
}
DEFAULT_OFFSETS: tuple[int, ...] = (0, 20, 40, 60, 80)


def _sha256(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _constant(
    curve_id: int,
    xs: list[float],
    value: float,
) -> tuple[list[dict[str, float | int]], int]:
    """Return a constant feature curve and the next curve id."""
    return (
        [{"curve_id": curve_id, "x": float(x), "y": float(value)} for x in xs],
        curve_id + 1,
    )


def _shift(
    frame: pd.DataFrame,
    *,
    curve_id: int,
    shift: float,
    year_floor: float = 0.0,
) -> list[dict[str, float | int]]:
    """Return a shifted FVS curve."""
    selected = frame[frame["Year"] >= year_floor].sort_values("Year")
    return [
        {"curve_id": curve_id, "x": float(shift + row.Year), "y": float(row.MCuM)}
        for row in selected.itertuples(index=False)
    ]


def _cuts(
    frame: pd.DataFrame,
    *,
    au: int,
    treatment: str,
    shift: float,
    curve_id: int,
) -> tuple[list[dict[str, float | int]], dict[str, int]]:
    """Return shifted total/sawlog/pulp cut curves."""
    selected = frame[(frame["au"] == au) & (frame["treatment"] == treatment)].copy()
    if selected.empty:
        return [], {}
    selected["volume_ha"] = selected["MCuM"].astype(float) * selected["TPH"].astype(float)
    selected["sawlog"] = selected["volume_ha"].where(selected["DBH"] >= 20.0, 0.0)
    selected["pulp"] = selected["volume_ha"].where(selected["DBH"] < 20.0, 0.0)
    grouped = (
        selected.groupby("Year", observed=True)
        .agg(total=("volume_ha", "sum"), sawlog=("sawlog", "sum"), pulp=("pulp", "sum"))
        .reset_index()
        .sort_values("Year")
    )
    rows: list[dict[str, float | int]] = []
    ids: dict[str, int] = {}
    for label, column in (
        ("product.harvest.total", "total"),
        ("product.harvest.sawlog", "sawlog"),
        ("product.harvest.pulp", "pulp"),
    ):
        ids[label] = curve_id
        for record in grouped.itertuples(index=False):
            rows.append(
                {
                    "curve_id": curve_id,
                    "x": float(shift + record.Year),
                    "y": float(getattr(record, column)),
                }
            )
        curve_id += 1
    return rows, ids


def build_dataset(
    *,
    curves_path: Path,
    cuts_path: Path,
    vri_path: Path,
    fragments_path: Path,
    blocks_path: Path,
    tracks_path: Path,
    tree_trajectories_path: Path,
    regen_curves_path: Path,
    extended_curves_path: Path,
    out_dir: Path,
    offsets: tuple[int, ...],
    bin_width: int = 10,
) -> Path:
    """Write the entry-age cohort graph."""
    curves = pd.read_csv(curves_path)
    cuts = pd.read_parquet(cuts_path)
    vri = gpd.read_file(vri_path)[["RES_KEY", "vri_age_2025", "vri_area_ha"]]
    fragments = pd.read_parquet(fragments_path)
    blocks = pd.read_parquet(blocks_path)
    tracks = pd.read_parquet(tracks_path)
    tree_trajectories = (
        pd.read_parquet(
            tree_trajectories_path,
            columns=["au", "treatment", "Year", "DBH", "TPH", "MCuM"],
        )
        if tree_trajectories_path.exists()
        else pd.DataFrame()
    )
    regen = pd.read_csv(regen_curves_path) if regen_curves_path.exists() else pd.DataFrame()
    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    block_au = (
        blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
        .dropna(subset=["au"])
        .set_index("block_id")["au"]
    )
    fragments = fragments.merge(vri, left_on="block_id", right_on="RES_KEY", how="left")
    fragments["au"] = fragments["block_id"].map(block_au)
    fragments = fragments.dropna(subset=["au"]).copy()
    fragments = fragments[fragments["au"].astype(int) != 9999].copy()
    fragments["age"] = fragments["vri_age_2025"].fillna(fragments["age"]).round().astype(int)
    fragments["bin_age"] = (fragments["age"] // bin_width) * bin_width
    fragments["area_ha"] = fragments["vri_area_ha"].fillna(fragments["area_ha"]).astype(float)

    out_dir.mkdir(parents=True, exist_ok=True)
    tracks_json: list[dict[str, object]] = []
    strata_json: list[dict[str, object]] = []
    treatments_json: list[dict[str, object]] = []
    curves_json: list[dict[str, float | int]] = []
    features_json: list[dict[str, object]] = []
    products_json: list[dict[str, object]] = []
    fragment_json: list[dict[str, object]] = []
    block_json: list[dict[str, object]] = []

    track_id = 1
    curve_id = 1
    for (au, bin_age), group in fragments.groupby(["au", "bin_age"], observed=True):
        au = int(au)
        bin_age = int(bin_age)
        untreated = track_id
        tracks_json.append({"track_id": untreated, "name": f"AU{au} age{bin_age} untreated"})
        strata_json.append({"track_id": untreated, "offset": 0, "next_age": 0, "cycle": 0})
        untreated_rows = _shift(
            curves[(curves["au"] == au) & (curves["treatment"] == "untreated")],
            curve_id=curve_id,
            shift=float(bin_age),
        )
        untreated_curve = curve_id
        curves_json.extend(untreated_rows)
        curve_id += 1
        area_rows, curve_id = _constant(
            curve_id,
            [float(row["x"]) for row in untreated_rows],
            1.0,
        )
        area_curve = int(area_rows[0]["curve_id"])
        curves_json.extend(area_rows)
        features_json.extend(
            [
                {
                    "track_id": untreated,
                    "label": "feature.area.managed.total",
                    "curve_id": area_curve,
                },
                {
                    "track_id": untreated,
                    "label": "feature.yield.managed.total",
                    "curve_id": untreated_curve,
                },
            ]
        )
        track_id += 1

        for treatment, display in TREATMENT_LABELS.items():
            source = curves[(curves["au"] == au) & (curves["treatment"] == treatment)]
            if source.empty:
                continue
            for offset in offsets:
                if offset > 90:
                    continue
                entry_age = bin_age + offset
                track = track_id
                tracks_json.append(
                    {
                        "track_id": track,
                        "name": f"AU{au} age{bin_age} {treatment} entry{offset}",
                    }
                )
                strata_json.append({"track_id": track, "offset": 0, "next_age": 0, "cycle": 0})
                treatments_json.append(
                    {
                        "track_id": untreated,
                        "begin": 0,
                        "end": 999,
                        "treatment": f"{display}_E{offset}",
                        "new_track": track,
                        "offset": entry_age,
                        "retain": 0,
                    }
                )
                yield_rows = _shift(
                    source,
                    curve_id=curve_id,
                    shift=float(entry_age - 10),
                    year_floor=10.0,
                )
                yield_curve = curve_id
                curves_json.extend(yield_rows)
                curve_id += 1
                area_rows, curve_id = _constant(
                    curve_id,
                    [float(row["x"]) for row in yield_rows],
                    1.0,
                )
                area_curve = int(area_rows[0]["curve_id"])
                curves_json.extend(area_rows)
                features_json.extend(
                    [
                        {
                            "track_id": track,
                            "label": "feature.area.managed.total",
                            "curve_id": area_curve,
                        },
                        {
                            "track_id": track,
                            "label": "feature.yield.managed.total",
                            "curve_id": yield_curve,
                        },
                    ]
                )
                cut_rows, cut_ids = _cuts(
                    cuts,
                    au=au,
                    treatment=treatment,
                    shift=float(entry_age),
                    curve_id=curve_id,
                )
                curves_json.extend(cut_rows)
                for label, cut_curve in cut_ids.items():
                    products_json.append(
                        {
                            "track_id": untreated,
                            "treatment": f"{display}_E{offset}",
                            "label": label,
                            "curve_id": cut_curve,
                        }
                    )
                if cut_ids:
                    curve_id += len(cut_ids)
                track_id += 1

        if not tree_trajectories.empty:
            untreated_trees = tree_trajectories[
                (tree_trajectories["au"] == au) & (tree_trajectories["treatment"] == "untreated")
            ]
            for offset in offsets:
                entry_age = bin_age + offset
                selected = untreated_trees[untreated_trees["Year"] == offset].copy()
                if selected.empty:
                    continue
                selected["volume_ha"] = selected["MCuM"].astype(float) * selected["TPH"].astype(
                    float
                )
                total = float(selected["volume_ha"].sum())
                sawlog = float(selected.loc[selected["DBH"] >= 20.0, "volume_ha"].sum())
                pulp = max(0.0, total - sawlog)
                if total <= 0.0:
                    continue
                track = track_id
                tracks_json.append(
                    {
                        "track_id": track,
                        "name": f"AU{au} age{bin_age} clearcut entry{offset}",
                    }
                )
                strata_json.append({"track_id": track, "offset": 0, "next_age": 0, "cycle": 0})
                treatments_json.append(
                    {
                        "track_id": untreated,
                        "begin": 0,
                        "end": 999,
                        "treatment": f"CLEARCUT_E{offset}",
                        "new_track": track,
                        "offset": entry_age,
                        "retain": 0,
                    }
                )
                regen_source = regen[regen["au"] == au].sort_values("Year")
                if regen_source.empty:
                    continue
                regen_rows = [
                    {
                        "curve_id": curve_id,
                        "x": float(entry_age + row.Year),
                        "y": float(row.MCuM),
                    }
                    for row in regen_source.itertuples(index=False)
                ]
                regen_curve = curve_id
                curves_json.extend(regen_rows)
                curve_id += 1
                area_rows, curve_id = _constant(
                    curve_id,
                    [float(row["x"]) for row in regen_rows],
                    1.0,
                )
                area_curve = int(area_rows[0]["curve_id"])
                curves_json.extend(area_rows)
                features_json.extend(
                    [
                        {
                            "track_id": track,
                            "label": "feature.area.managed.total",
                            "curve_id": area_curve,
                        },
                        {
                            "track_id": track,
                            "label": "feature.yield.managed.total",
                            "curve_id": regen_curve,
                        },
                    ]
                )
                for label, value in (
                    ("product.harvest.total", total),
                    ("product.harvest.sawlog", sawlog),
                    ("product.harvest.pulp", pulp),
                ):
                    product_curve = curve_id
                    curves_json.append(
                        {
                            "curve_id": product_curve,
                            "x": float(entry_age),
                            "y": float(value),
                        }
                    )
                    curve_id += 1
                    products_json.append(
                        {
                            "track_id": untreated,
                            "treatment": f"CLEARCUT_E{offset}",
                            "label": label,
                            "curve_id": product_curve,
                        }
                    )
                track_id += 1

        for row in group.itertuples(index=False):
            fragment_json.append(
                {
                    "fragment_id": int(row.fragment_id),
                    "block_id": int(row.block_id),
                    "area_ha": float(row.area_ha),
                    "age": int(row.age),
                    "track_id": untreated,
                }
            )

    block_area = pd.DataFrame(fragment_json).groupby("block_id")["area_ha"].sum()
    block_track: dict[int, int] = {}
    for row in fragment_json:
        block_track.setdefault(int(row["block_id"]), int(row["track_id"]))
    for block_id, area in block_area.items():
        block_json.append(
            {
                "block_id": int(block_id),
                "track_id": block_track[int(block_id)],
                "offset": 0,
                "area_ha": float(area),
            }
        )

    frames = {
        "fragments": pd.DataFrame(fragment_json),
        "blocks": pd.DataFrame(block_json),
        "tracks": pd.DataFrame(tracks_json),
        "strata": pd.DataFrame(strata_json),
        "treatments": pd.DataFrame(treatments_json),
        "curves": pd.DataFrame(curves_json),
        "features": pd.DataFrame(features_json),
        "products": pd.DataFrame(products_json),
        "accounts": pd.DataFrame(columns=["group", "attribute", "account", "sum"]),
        "protoaccounts": pd.DataFrame(columns=["group", "attribute", "account", "sum"]),
        "groups": pd.DataFrame(
            [{"block_id": int(row["block_id"]), "group": "forest"} for row in fragment_json]
        ),
        "messages": pd.DataFrame(columns=["severity", "message"]),
    }
    for name, table in TABLES_BY_NAME.items():
        frame = frames.get(name, pd.DataFrame(columns=table.required_columns))
        coerce_to_schema(frame, table).to_parquet(out_dir / table.file, index=False)

    manifest = CanonicalDatasetManifest(
        schema_version=SCHEMA_VERSION,
        tables={table.name: table.file for table in TABLES_BY_NAME.values()},
        sources=[
            {"path": curves_path.name, "sha256": _sha256(curves_path)},
            {"path": cuts_path.name, "sha256": _sha256(cuts_path)},
        ],
        options={
            "period_length": 1,
            "ingest": "fvsbc-entry-age-cohort-graph",
            "bin_width": bin_width,
            "entry_offsets": list(offsets),
            "entry": "one",
        },
        metadata={
            "scope": "Gavin Lake productive fragments",
            "caveats": [
                "One treatment entry per fragment, at a chosen 20-year offset.",
                "FVS curves shifted from the AU entry age to the bin age and offset.",
                "Clearcut enters a planted bare-ground regeneration curve; "
                "no natural ingress or fire.",
            ],
        },
    )
    (out_dir / MANIFEST_NAME).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return out_dir


def main() -> None:
    """Build the cohort graph."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curves", type=Path, default=Path("data/fvsbc/gl_all/curves.csv"))
    parser.add_argument("--cuts", type=Path, default=Path("data/fvsbc/gl_all/cut_list.parquet"))
    parser.add_argument(
        "--vri", type=Path, default=Path("data/inventory/gavin_vri_2025_start.gpkg")
    )
    parser.add_argument(
        "--fragments", type=Path, default=Path("ws4/runtime/legacy_matrix/fragments.parquet")
    )
    parser.add_argument(
        "--blocks", type=Path, default=Path("ws4/runtime/legacy_matrix/blocks.parquet")
    )
    parser.add_argument(
        "--tracks", type=Path, default=Path("ws4/runtime/legacy_matrix/tracks.parquet")
    )
    parser.add_argument(
        "--tree-trajectories",
        type=Path,
        default=Path("data/fvsbc/gl_all/tree_trajectories.parquet"),
    )
    parser.add_argument(
        "--regen-curves",
        type=Path,
        default=Path("data/fvsbc/gl_regen/regen_curves.csv"),
    )
    parser.add_argument(
        "--extended-curves",
        type=Path,
        default=Path("data/fvsbc/gl_untreated_200y/curves.csv"),
    )
    parser.add_argument("--out", type=Path, default=Path("ws4/runtime/fvsbc_cohort_graph"))
    parser.add_argument("--offsets", default="0,20,40,60,80")
    parser.add_argument("--bin-width", type=int, default=10)
    args = parser.parse_args()
    offsets = tuple(int(value) for value in args.offsets.split(",") if value.strip())
    result = build_dataset(
        curves_path=args.curves,
        cuts_path=args.cuts,
        vri_path=args.vri,
        fragments_path=args.fragments,
        blocks_path=args.blocks,
        tracks_path=args.tracks,
        tree_trajectories_path=args.tree_trajectories,
        regen_curves_path=args.regen_curves,
        extended_curves_path=args.extended_curves,
        out_dir=args.out,
        offsets=offsets,
        bin_width=args.bin_width,
    )
    print(result)


if __name__ == "__main__":
    main()

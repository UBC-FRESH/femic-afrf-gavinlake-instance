#!/usr/bin/env python3
"""Compile the 2,907-fragment Gavin Lake FVS-BC ws4 graph.

Each fragment is assigned to an age-binned track for its AU. The FVS-BC curve is
shifted from the AU's entry age to the bin's age, so a young fragment does not
inherit an old AU's volume. The first and second entries are carried as treatment
edges from the untreated bin track.
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

SECOND_ENTRY_TREATMENTS = frozenset({"ct60", "selection80"})


def _sha256(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _constant_curve(
    curve_id: int,
    x_values: list[float],
    value: float,
) -> tuple[list[dict[str, float | int]], int]:
    """Return a constant curve and the next curve id."""
    return (
        [{"curve_id": curve_id, "x": float(x), "y": float(value)} for x in x_values],
        curve_id + 1,
    )


def _shift_curve(
    frame: pd.DataFrame,
    *,
    curve_id: int,
    shift: float,
    year_floor: float = 0.0,
) -> list[dict[str, float | int]]:
    """Return a FVS curve shifted to the bin age."""
    selected = frame[frame["Year"] >= year_floor].sort_values("Year")
    return [
        {"curve_id": curve_id, "x": float(shift + row.Year), "y": float(row.MCuM)}
        for row in selected.itertuples(index=False)
    ]


def _cut_products(
    cuts: pd.DataFrame,
    *,
    au: int,
    treatment: str,
    shift: float,
    curve_id: int,
) -> tuple[list[dict[str, float | int]], dict[str, int]]:
    """Return total, sawlog, and pulp harvest curves for one bin/treatment."""
    selected = cuts[(cuts["au"] == au) & (cuts["treatment"] == treatment)].copy()
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
    runs_path: Path,
    cuts_path: Path,
    second_entry_path: Path,
    second_cuts_path: Path,
    vri_path: Path,
    fragments_path: Path,
    blocks_path: Path,
    tracks_path: Path,
    out_dir: Path,
    bin_width: int = 10,
) -> Path:
    """Write the age-binned spatial ws4 graph."""
    curves = pd.read_csv(curves_path)
    second = pd.read_csv(second_entry_path)
    cuts = pd.read_parquet(cuts_path)
    second_cuts = pd.read_parquet(second_cuts_path)
    runs = pd.read_csv(runs_path).drop_duplicates("au").set_index("au")
    vri = gpd.read_file(vri_path)[["RES_KEY", "vri_age_2025", "vri_area_ha"]]
    fragments = pd.read_parquet(fragments_path)
    blocks = pd.read_parquet(blocks_path)
    tracks = pd.read_parquet(tracks_path)

    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    block_au = (
        blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
        .dropna(subset=["au"])
        .set_index("block_id")["au"]
    )
    fragments = fragments.merge(
        vri,
        left_on="block_id",
        right_on="RES_KEY",
        how="left",
    )
    fragments["au"] = fragments["block_id"].map(block_au)
    fragments = fragments.dropna(subset=["au"])
    fragments = fragments[fragments["au"].astype(int) != 9999].copy()
    fragments["age"] = fragments["vri_age_2025"].fillna(fragments["age"]).round().astype(int)
    fragments["bin_age"] = (fragments["age"] // bin_width) * bin_width
    fragments["area_ha"] = fragments["vri_area_ha"].fillna(fragments["area_ha"]).astype(float)

    out_dir.mkdir(parents=True, exist_ok=True)
    track_rows: list[dict[str, object]] = []
    strata_rows: list[dict[str, object]] = []
    treatment_rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, float | int]] = []
    feature_rows: list[dict[str, object]] = []
    product_rows: list[dict[str, object]] = []
    fragment_rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []

    track_id = 1
    curve_id = 1
    track_for: dict[tuple[int, int, str, int], int] = {}
    for (au, bin_age), group in fragments.groupby(["au", "bin_age"], observed=True):
        au = int(au)
        bin_age = int(bin_age)
        if au not in runs.index:
            continue
        source = curves[curves["au"] == au]
        second_source = second[second["au"] == au]
        # Untreated bin track.
        untreated = track_id
        track_for[(au, bin_age, "untreated", 1)] = untreated
        track_rows.append({"track_id": untreated, "name": f"AU{au} age{bin_age} untreated"})
        strata_rows.append({"track_id": untreated, "offset": 0, "next_age": 0, "cycle": 0})
        untreated_rows = _shift_curve(
            source[source["treatment"] == "untreated"],
            curve_id=curve_id,
            shift=float(bin_age),
        )
        untreated_curve = curve_id
        curve_rows.extend(untreated_rows)
        curve_id += 1
        area_rows, curve_id = _constant_curve(
            curve_id,
            [float(row["x"]) for row in untreated_rows],
            1.0,
        )
        area_curve = int(area_rows[0]["curve_id"])
        curve_rows.extend(area_rows)
        feature_rows.extend(
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

        for treatment in ["ct60", "fuel50", "selection80", "shelterwood40", "vr20"]:
            source_treatment = source[source["treatment"] == treatment]
            if source_treatment.empty:
                continue
            first_track = track_id
            track_for[(au, bin_age, treatment, 1)] = first_track
            track_rows.append(
                {"track_id": first_track, "name": f"AU{au} age{bin_age} {treatment} first"}
            )
            strata_rows.append({"track_id": first_track, "offset": 0, "next_age": 0, "cycle": 0})
            treatment_rows.append(
                {
                    "track_id": untreated,
                    "begin": 0,
                    "end": 999,
                    "treatment": TREATMENT_LABELS[treatment],
                    "new_track": first_track,
                    "offset": bin_age,
                    "retain": 0,
                }
            )
            first_rows = _shift_curve(
                source_treatment,
                curve_id=curve_id,
                shift=float(bin_age - 10),
                year_floor=10.0,
            )
            first_curve = curve_id
            curve_rows.extend(first_rows)
            curve_id += 1
            first_area, curve_id = _constant_curve(
                curve_id,
                [float(row["x"]) for row in first_rows],
                1.0,
            )
            first_area_curve = int(first_area[0]["curve_id"])
            curve_rows.extend(first_area)
            feature_rows.extend(
                [
                    {
                        "track_id": first_track,
                        "label": "feature.area.managed.total",
                        "curve_id": first_area_curve,
                    },
                    {
                        "track_id": first_track,
                        "label": "feature.yield.managed.total",
                        "curve_id": first_curve,
                    },
                ]
            )
            cut_rows, cut_ids = _cut_products(
                cuts,
                au=au,
                treatment=treatment,
                shift=float(bin_age),
                curve_id=curve_id,
            )
            curve_rows.extend(cut_rows)
            for label, cut_curve in cut_ids.items():
                product_rows.append(
                    {
                        "track_id": untreated,
                        "treatment": TREATMENT_LABELS[treatment],
                        "label": label,
                        "curve_id": cut_curve,
                    }
                )
            if cut_ids:
                curve_id += len(cut_ids)
            track_id += 1

            if treatment in SECOND_ENTRY_TREATMENTS and not second_source.empty:
                second_track = track_id
                track_for[(au, bin_age, treatment, 2)] = second_track
                track_rows.append(
                    {
                        "track_id": second_track,
                        "name": f"AU{au} age{bin_age} {treatment} second",
                    }
                )
                strata_rows.append(
                    {"track_id": second_track, "offset": 0, "next_age": 0, "cycle": 0}
                )
                treatment_rows.append(
                    {
                        "track_id": first_track,
                        "begin": 0,
                        "end": 999,
                        "treatment": TREATMENT_LABELS[treatment],
                        "new_track": second_track,
                        "offset": bin_age + 10,
                        "retain": 0,
                    }
                )
                second_rows = _shift_curve(
                    second_source[second_source["treatment"] == treatment],
                    curve_id=curve_id,
                    shift=float(bin_age + 10),
                )
                second_curve = curve_id
                curve_rows.extend(second_rows)
                curve_id += 1
                second_area, curve_id = _constant_curve(
                    curve_id,
                    [float(row["x"]) for row in second_rows],
                    1.0,
                )
                second_area_curve = int(second_area[0]["curve_id"])
                curve_rows.extend(second_area)
                feature_rows.extend(
                    [
                        {
                            "track_id": second_track,
                            "label": "feature.area.managed.total",
                            "curve_id": second_area_curve,
                        },
                        {
                            "track_id": second_track,
                            "label": "feature.yield.managed.total",
                            "curve_id": second_curve,
                        },
                    ]
                )
                second_cut_rows, second_cut_ids = _cut_products(
                    second_cuts,
                    au=au,
                    treatment=treatment,
                    shift=float(bin_age + 10),
                    curve_id=curve_id,
                )
                curve_rows.extend(second_cut_rows)
                for label, cut_curve in second_cut_ids.items():
                    product_rows.append(
                        {
                            "track_id": first_track,
                            "treatment": TREATMENT_LABELS[treatment],
                            "label": label,
                            "curve_id": cut_curve,
                        }
                    )
                if second_cut_ids:
                    curve_id += len(second_cut_ids)
                track_id += 1

        for fragment in group.itertuples(index=False):
            fragment_rows.append(
                {
                    "fragment_id": int(fragment.fragment_id),
                    "block_id": int(fragment.block_id),
                    "area_ha": float(fragment.area_ha),
                    "age": int(fragment.age),
                    "track_id": untreated,
                }
            )

    block_area = pd.DataFrame(fragment_rows).groupby("block_id")["area_ha"].sum()
    block_track: dict[int, int] = {}
    for row in fragment_rows:
        block_track.setdefault(int(row["block_id"]), int(row["track_id"]))
    for block_id, area in block_area.items():
        block_rows.append(
            {
                "block_id": int(block_id),
                "track_id": block_track[int(block_id)],
                "offset": 0,
                "area_ha": float(area),
            }
        )

    frames = {
        "fragments": pd.DataFrame(fragment_rows),
        "blocks": pd.DataFrame(block_rows),
        "tracks": pd.DataFrame(track_rows),
        "strata": pd.DataFrame(strata_rows),
        "treatments": pd.DataFrame(treatment_rows),
        "curves": pd.DataFrame(curve_rows),
        "features": pd.DataFrame(feature_rows),
        "products": pd.DataFrame(product_rows),
        "accounts": pd.DataFrame(columns=["group", "attribute", "account", "sum"]),
        "protoaccounts": pd.DataFrame(columns=["group", "attribute", "account", "sum"]),
        "groups": pd.DataFrame(
            [{"block_id": int(row["block_id"]), "group": "forest"} for row in fragment_rows]
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
            {"path": runs_path.name, "sha256": _sha256(runs_path)},
            {"path": vri_path.name, "sha256": _sha256(vri_path)},
        ],
        options={
            "period_length": 1,
            "ingest": "fvsbc-age-binned-spatial-graph",
            "bin_width": bin_width,
            "entry": "two",
        },
        metadata={
            "scope": "Gavin Lake productive fragments",
            "caveats": [
                "Fragments are assigned to 10-year age bins inside each AU.",
                "FVS curves are shifted from the AU entry age to the bin age.",
                "Two entries only; no regeneration, fire, or climate extension.",
            ],
        },
    )
    (out_dir / MANIFEST_NAME).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return out_dir


def main() -> None:
    """Build the age-binned spatial graph."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curves", type=Path, default=Path("data/fvsbc/gl_all/curves.csv"))
    parser.add_argument("--runs", type=Path, default=Path("data/fvsbc/gl_all/runs.csv"))
    parser.add_argument("--cuts", type=Path, default=Path("data/fvsbc/gl_all/cut_list.parquet"))
    parser.add_argument(
        "--second-entry",
        type=Path,
        default=Path("data/fvsbc/gl_multientry/second_entry_curves.csv"),
    )
    parser.add_argument(
        "--second-cuts",
        type=Path,
        default=Path("data/fvsbc/gl_multientry/second_entry_cuts.parquet"),
    )
    parser.add_argument(
        "--vri",
        type=Path,
        default=Path("data/inventory/gavin_vri_2025_start.gpkg"),
    )
    parser.add_argument(
        "--fragments",
        type=Path,
        default=Path("ws4/runtime/legacy_matrix/fragments.parquet"),
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
        "--out",
        type=Path,
        default=Path("ws4/runtime/fvsbc_spatial_graph"),
    )
    parser.add_argument("--bin-width", type=int, default=10)
    args = parser.parse_args()
    result = build_dataset(
        curves_path=args.curves,
        runs_path=args.runs,
        cuts_path=args.cuts,
        second_entry_path=args.second_entry,
        second_cuts_path=args.second_cuts,
        vri_path=args.vri,
        fragments_path=args.fragments,
        blocks_path=args.blocks,
        tracks_path=args.tracks,
        out_dir=args.out,
        bin_width=args.bin_width,
    )
    print(result)


if __name__ == "__main__":
    main()

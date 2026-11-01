#!/usr/bin/env python3
"""Compile the FVS-BC AU library into a ws4-compatible state graph.

The graph is a **single-entry v0**:

- one fragment per AU, on the untreated track at the VRI age;
- one track per AU/treatment;
- a treatment edge from the untreated track to each treatment track at the AU's
  current age;
- the treatment curve starts at the post-treatment FVS cycle (year 10), shifted
  back to the AU's current age.

This is a valid ws4 dataset for a single entry per AU. It is not a multi-entry
selection model; repeated entries need age-specific tracks.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd
from ws4.model.schema import MANIFEST_NAME, SCHEMA_VERSION, TABLES_BY_NAME, coerce_to_schema
from ws4.model.types import CanonicalDatasetManifest

#: Treatment labels in the ws4 schedule.
TREATMENT_LABELS: dict[str, str] = {
    "ct60": "CT60",
    "fuel50": "FUEL50",
    "selection80": "SELECTION80",
    "shelterwood40": "SHELTERWOOD40",
    "vr20": "VR20",
}


def _sha256(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _curves_for_track(
    *,
    track_id: int,
    curve_id: int,
    source: pd.DataFrame,
    age: float,
    treatment: str,
) -> tuple[list[dict[str, float | int]], int]:
    """Build one track's yield curve and return its next curve id."""
    rows: list[dict[str, float | int]] = []
    if treatment == "untreated":
        selected = source[source["treatment"] == "untreated"]
        for row in selected.itertuples(index=False):
            rows.append(
                {
                    "curve_id": curve_id,
                    "x": float(age + float(row.Year)),
                    "y": float(row.MCuM),
                }
            )
    else:
        # The FVS treatment is applied in cycle 1 and the post-treatment state is
        # first observed in cycle 2 (year 10). Shift that state back to the entry age.
        selected = source[(source["treatment"] == treatment) & (source["Year"] >= 10)]
        for row in selected.itertuples(index=False):
            rows.append(
                {
                    "curve_id": curve_id,
                    "x": float(age + float(row.Year) - 10.0),
                    "y": float(row.MCuM),
                }
            )
    return rows, curve_id + 1


def _constant_curve(
    *,
    curve_id: int,
    x_values: list[float],
    value: float,
) -> tuple[list[dict[str, float | int]], int]:
    """Build one constant feature curve and return its next curve id."""
    return (
        [{"curve_id": curve_id, "x": float(x), "y": float(value)} for x in x_values],
        curve_id + 1,
    )


def build_dataset(
    *,
    curves_path: Path,
    runs_path: Path,
    out_dir: Path,
    aus: tuple[int, ...] | None = None,
) -> Path:
    """Write a ws4-compatible single-entry state graph.

    Parameters
    ----------
    curves_path : Path
        The FVS `curves.csv`.
    runs_path : Path
        The FVS `runs.csv`.
    out_dir : Path
        Output dataset directory.
    aus : tuple of int, optional
        AU subset; default is every AU in the run table.

    Returns
    -------
    Path
        The dataset directory.
    """
    curves = pd.read_csv(curves_path)
    runs = pd.read_csv(runs_path).drop_duplicates("au")
    if aus is not None:
        curves = curves[curves["au"].isin(aus)]
        runs = runs[runs["au"].isin(aus)]
    out_dir.mkdir(parents=True, exist_ok=True)

    track_rows: list[dict[str, object]] = []
    fragment_rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    treatment_rows: list[dict[str, object]] = []
    strata_rows: list[dict[str, object]] = []
    curve_rows: list[dict[str, float | int]] = []
    feature_rows: list[dict[str, object]] = []
    product_rows: list[dict[str, object]] = []

    track_id = 1
    curve_id = 1
    for run in runs.sort_values("au").itertuples(index=False):
        au = int(run.au)
        age = round(float(run.tree_age))
        area = float(run.area_ha)
        source = curves[curves["au"] == au]
        untreated_track = track_id
        track_rows.append({"track_id": untreated_track, "name": f"AU{au} untreated"})
        strata_rows.append({"track_id": untreated_track, "offset": 0, "next_age": 0, "cycle": 0})
        track_id += 1
        fragment_rows.append(
            {
                "fragment_id": au,
                "block_id": au,
                "area_ha": area,
                "age": age,
                "track_id": untreated_track,
            }
        )
        block_rows.append(
            {"block_id": au, "track_id": untreated_track, "offset": 0, "area_ha": area}
        )

        treatment_track_ids: dict[str, int] = {}
        for treatment in ["untreated", *TREATMENT_LABELS]:
            if treatment == "untreated":
                this_track = untreated_track
            else:
                this_track = track_id
                treatment_track_ids[treatment] = this_track
                track_rows.append({"track_id": this_track, "name": f"AU{au} {treatment}"})
                strata_rows.append({"track_id": this_track, "offset": 0, "next_age": 0, "cycle": 0})
                treatment_rows.append(
                    {
                        "track_id": untreated_track,
                        "begin": 0,
                        "end": 999,
                        "treatment": TREATMENT_LABELS[treatment],
                        "new_track": this_track,
                        "offset": age,
                        "retain": 0,
                    }
                )
                track_id += 1
            new_curve_rows, curve_id = _curves_for_track(
                track_id=this_track,
                curve_id=curve_id,
                source=source,
                age=age,
                treatment=treatment,
            )
            yield_curve = int(new_curve_rows[0]["curve_id"])
            curve_rows.extend(new_curve_rows)
            x_values = [float(row["x"]) for row in new_curve_rows]
            area_rows, curve_id = _constant_curve(
                curve_id=curve_id,
                x_values=x_values,
                value=1.0,
            )
            area_curve = int(area_rows[0]["curve_id"])
            curve_rows.extend(area_rows)
            feature_rows.append(
                {
                    "track_id": this_track,
                    "label": "feature.area.managed.total",
                    "curve_id": area_curve,
                }
            )
            feature_rows.append(
                {
                    "track_id": this_track,
                    "label": "feature.yield.managed.total",
                    "curve_id": yield_curve,
                }
            )
            product_rows.append(
                {
                    "track_id": this_track,
                    "treatment": "CC",
                    "label": "product.yield.managed.total",
                    "curve_id": yield_curve,
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
        ],
        options={
            "period_length": 1,
            "ingest": "fvsbc-au-state-graph",
            "entry": "single",
            "treatment_time": "entry age",
        },
        metadata={
            "scope": "Gavin Lake productive AUs",
            "caveats": [
                "Single-entry v0 graph; repeated entries need age-specific tracks.",
                "AU fragments are aggregated at the AU scale.",
                "FVS treatment curves are shifted from cycle 2 to the entry age.",
            ],
        },
    )
    (out_dir / MANIFEST_NAME).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return out_dir


def main() -> None:
    """Build the ws4 state graph from the full FVS-BC curve table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--curves",
        type=Path,
        default=Path("data/fvsbc/gl_all/curves.csv"),
    )
    parser.add_argument(
        "--runs",
        type=Path,
        default=Path("data/fvsbc/gl_all/runs.csv"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("ws4/runtime/fvsbc_state_graph"),
    )
    parser.add_argument("--aus", default="")
    args = parser.parse_args()
    aus = tuple(int(value) for value in args.aus.split(",") if value.strip()) or None
    result = build_dataset(
        curves_path=args.curves,
        runs_path=args.runs,
        out_dir=args.out,
        aus=aus,
    )
    print(result)


if __name__ == "__main__":
    main()

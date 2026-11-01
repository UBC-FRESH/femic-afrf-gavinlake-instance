#!/usr/bin/env python3
"""Build the six-AU Gavin Lake FVS-BC creative-silviculture pilot.

The pilot links the 2025 VRI species/age layer to the full 2009 Gavin Lake
canopy inventory and can build a species-resolved tree list for the six-AU
pilot or for every productive AU. It runs FVS-BC for an untreated baseline
and five partial-harvest prescriptions.

The FVS-BC keyword targets are metric: the BC variant reads ``THINBBA`` and
``THINABA`` basal-area targets in m2/ha, not the imperial units in the US FVS
keyword guide. A target above the standing basal area is silently cancelled, so
the targets here are fractions of the sampled initial basal area.

Usage::

    python runbooks/build_gl_fvsbc_pilot.py
    python runbooks/build_gl_fvsbc_pilot.py --all-aus
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import shutil
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from fresh_fvsbc.keywords import Keyword
    from fresh_fvsbc.run import RunResult

#: Six AUs spanning the ICH/SBS and age/species gradient. Chosen from the
#: 80 productive AUs; AU 9999 is the non-productive/unclassified group.
PILOT_AUS: tuple[int, ...] = (2, 302, 352, 312, 802, 502)

#: Partial-harvest prescriptions. The fraction is the residual basal area.
TREATMENTS: dict[str, float | None] = {
    "untreated": None,
    "ct60": 0.60,
    "fuel50": 0.50,
    "selection80": 0.80,
    "shelterwood40": 0.40,
    "vr20": 0.20,
}

#: Species mapping from VRI species columns to FVS-BC JSP codes.
SPECIES_MAP: dict[str, str] = {
    "FD": "FD",
    "FDI": "FD",
    "SX": "SE",
    "CW": "CW",
    "PL": "PL",
    "PLI": "PL",
    "BL": "BL",
    "AT": "AT",
    "AC": "AC",
    "ACT": "AC",
    "EP": "EP",
}

#: Screening site index (BC uses metres; FVS-BC converts internally).
SITE_INDEX: dict[str, float] = {
    "FD": 100.0,
    "SE": 90.0,
    "CW": 90.0,
    "PL": 100.0,
    "BL": 80.0,
    "AT": 90.0,
    "AC": 90.0,
    "EP": 80.0,
}


def _require_fvsbc() -> tuple[object, object, object]:
    """Import the FVS-BC API only when a run is requested."""
    from fresh_fvsbc.keywords import Keyword
    from fresh_fvsbc.outputs import read_table
    from fresh_fvsbc.run import run_case

    return Keyword, read_table, run_case


def _au_table(
    vri: gpd.GeoDataFrame,
    blocks: pd.DataFrame,
    tracks: pd.DataFrame,
) -> pd.DataFrame:
    """Return one area-weighted row per AU.

    Parameters
    ----------
    vri : geopandas.GeoDataFrame
        The 2025 VRI starting layer.
    blocks : pandas.DataFrame
        The legacy block table, with ``block_id``, ``track_id`` and ``area_ha``.
    tracks : pandas.DataFrame
        The legacy track table, with ``track_id`` and ``name``.

    Returns
    -------
    pandas.DataFrame
        AU area, age, BEC, species shares, and tree density.
    """
    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    merged = blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
    merged = merged.merge(
        vri[
            [
                "RES_KEY",
                "vri_age_2025",
                "BEC",
                "vri_area_ha",
                *[column for column in vri.columns if column.startswith("species_")],
            ]
        ],
        left_on="block_id",
        right_on="RES_KEY",
        how="left",
    )
    rows: list[dict[str, float | int | str]] = []
    for au, group in merged.groupby("au", dropna=True):
        weights = group["area_ha"].to_numpy(dtype=float)
        if weights.sum() <= 0.0:
            continue
        species: dict[str, float] = {}
        for column in [name for name in group.columns if name.startswith("species_")]:
            values = group[column].fillna(0.0).to_numpy(dtype=float)
            species[column.removeprefix("species_")] = float(np.average(values, weights=weights))
        row: dict[str, float | int | str] = {
            "au": int(au),
            "area_ha": float(weights.sum()),
            "age_2025": float(np.average(group["vri_age_2025"].fillna(0.0), weights=weights)),
            "bec": str(group["BEC"].mode().iloc[0]) if not group["BEC"].mode().empty else "",
        }
        row.update({f"share_{key}": value for key, value in species.items()})
        rows.append(row)
    return pd.DataFrame(rows).sort_values("au").reset_index(drop=True)


def _tree_au(
    trees: gpd.GeoDataFrame,
    vri: gpd.GeoDataFrame,
    blocks: pd.DataFrame,
    tracks: pd.DataFrame,
) -> gpd.GeoDataFrame:
    """Join the 2009 tree points to VRI blocks once and label each tree with its AU."""
    parsed = tracks.copy()
    parsed["au"] = parsed["name"].str.extract(r"au\((\d+)\)")[0].astype(float)
    block_au = (
        blocks.merge(parsed[["track_id", "au"]], on="track_id", how="left")
        .dropna(subset=["au"])
        .set_index("block_id")["au"]
    )
    joined = gpd.sjoin(
        trees,
        vri[["RES_KEY", "geometry"]],
        how="inner",
        predicate="within",
    )
    joined["au"] = joined["RES_KEY"].map(block_au)
    return joined.dropna(subset=["au"])


def _sample_rows(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    """Systematically sample a DBH-sorted frame to preserve its distribution."""
    if count >= len(frame):
        return frame.copy()
    ordered = frame.sort_values("dbh_cm_est").reset_index(drop=True)
    indexes = np.linspace(0, len(ordered) - 1, count).round().astype(int)
    return ordered.iloc[indexes].copy()


def _species_pool(shares: dict[str, float]) -> tuple[list[str], np.ndarray]:
    """Return mapped species codes and normalized probabilities."""
    codes: list[str] = []
    probabilities: list[float] = []
    for key, value in shares.items():
        code = SPECIES_MAP.get(key)
        if code is not None and value > 0.0:
            codes.append(code)
            probabilities.append(float(value))
    if not codes:
        raise ValueError("no mapped species in the VRI share")
    array = np.asarray(probabilities, dtype=float)
    return codes, array / array.sum()


def _assign_species(
    shares: dict[str, float],
    count: int,
    *,
    seed: int,
) -> list[str]:
    """Assign species codes to sampled trees with the VRI area shares."""
    codes, probabilities = _species_pool(shares)
    rng = np.random.default_rng(seed)
    return [str(code) for code in rng.choice(codes, size=count, p=probabilities)]


def _target_tph(
    tree_rows: pd.DataFrame,
    area_ha: float,
) -> float:
    """Return canopy-tree density (trees per hectare) for an AU."""
    return float(len(tree_rows) / area_ha) if area_ha > 0.0 else 0.0


def _density_plan(target_tph: float) -> tuple[int, int]:
    """Return sample size and integer expansion to represent ``target_tph``.

    The BC tree-count field is an integer. Choose an expansion from the density
    and then choose the sample size that reproduces the target with that
    expansion.
    """
    expansion = max(1, round(target_tph / 60.0))
    sample = round(target_tph / expansion) if target_tph > 0.0 else 30
    sample = max(30, min(120, sample))
    expansion = max(1, round(target_tph / sample)) if sample else 1
    return sample, expansion


def _tree_records(
    sample: pd.DataFrame,
    species: list[str],
    *,
    expansion: int,
    age: float,
) -> list[dict[str, float | int | str]]:
    """Build FVS-BC tree-list records for one plot."""
    records: list[dict[str, float | int | str]] = []
    for index, (_, row) in enumerate(sample.iterrows(), start=1):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": float(expansion),
                "tree_history": 0,
                "species": species[index - 1],
                "diam": float(row["dbh_cm_est"]),
                "dg_incr": 0.0,
                "live_ht": float(row["height_m"]),
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": 5,
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
    return records


def _initial_ba(records: Iterable[dict[str, float | int | str]]) -> float:
    """Return initial basal area in m2/ha from expanded tree records."""
    total = 0.0
    for record in records:
        diameter = float(record["diam"])
        count = float(record["tree_count"])
        total += math.pi * (diameter / 200.0) ** 2 * count
    return total


def _psp_plots(psp_dir: Path) -> pd.DataFrame:
    """Return plot-level BA, TPH, age, and BEC for the Williams Lake PSP set."""
    header = pd.read_csv(psp_dir / "faib_header.csv", low_memory=False)
    trees = pd.read_csv(psp_dir / "faib_tree_detail.csv", low_memory=False)
    header["BEC"] = (
        header["BEC_ZONE"].fillna("")
        + header["BEC_SBZ"].fillna("")
        + header["BEC_VAR"].fillna("").astype(str).str.replace(".0", "", regex=False)
    )
    detail = trees.merge(
        header[["SITE_IDENTIFIER", "TSA_DESC", "BEC"]],
        on="SITE_IDENTIFIER",
        how="left",
    )
    detail = detail[
        detail["TSA_DESC"].str.contains("Williams", na=False) & (detail["LV_D"] == "L")
    ].copy()
    detail["ba_ha"] = (
        detail["BA_TREE"].fillna(0.0)
        * detail["PHF_TREE"].fillna(0.0)
        * detail["TREE_WT"].fillna(1.0)
    )
    detail["tph"] = detail["PHF_TREE"].fillna(0.0) * detail["TREE_WT"].fillna(1.0)
    return (
        detail.groupby(["CLSTR_ID", "VISIT_NUMBER", "BEC"], dropna=False)
        .agg(
            ba_m2_ha=("ba_ha", "sum"),
            tph=("tph", "sum"),
            age_bh=("AGE_BH", "mean"),
        )
        .reset_index()
    )


def _psp_target(
    plots: pd.DataFrame,
    *,
    bec: str,
    age: float,
    window: int = 20,
) -> tuple[float, float, int]:
    """Return mean BA, mean age, and plot count for a BEC/age analog."""
    if plots.empty:
        return (float("nan"), float("nan"), 0)
    candidates = list(dict.fromkeys([bec, bec.split("/")[0]]))
    for candidate in candidates:
        for width in (window, window * 2, window * 3):
            selected = plots[
                (plots["BEC"] == candidate) & plots["age_bh"].between(age - width, age + width)
            ]
            if len(selected) >= 3:
                return (
                    float(selected["ba_m2_ha"].mean()),
                    float(selected["age_bh"].mean()),
                    len(selected),
                )
    # Mixed or unsupported BEC: fall back to the same TSA and age window.
    for width in (window, window * 2, window * 3):
        selected = plots[plots["age_bh"].between(age - width, age + width)]
        if len(selected) >= 3:
            return (
                float(selected["ba_m2_ha"].mean()),
                float(selected["age_bh"].mean()),
                len(selected),
            )
    return (float("nan"), float("nan"), 0)


def _site_species(shares: dict[str, float]) -> str:
    """Return the dominant mapped species, or FD when none is mapped."""
    codes, probabilities = _species_pool(shares)
    return codes[int(np.argmax(probabilities))]


def _treatment_keywords(
    name: str,
    residual_fraction: float | None,
    *,
    initial_ba: float,
) -> tuple[Keyword, ...]:
    """Return the FVS-BC treatment keywords for one prescription."""
    keyword_cls, _, _ = _require_fvsbc()
    if name == "untreated":
        return ()
    if residual_fraction is None:
        raise ValueError(f"treatment {name!r} needs a residual fraction")
    target = max(0.0, float(initial_ba) * residual_fraction)
    if name == "selection80":
        return tuple(
            keyword_cls("THINBBA", (str(year), f"{target:.2f}", "0.95", "0.0", "999.0", "0", "999"))
            for year in (1, 3, 5, 7, 9)
        )
    if name == "shelterwood40":
        return (
            keyword_cls("THINBBA", ("1", f"{target:.2f}", "0.95", "0.0", "999.0", "0", "999")),
            keyword_cls("THINBBA", ("4", "0.01", "0.95", "0.0", "999.0", "0", "999")),
        )
    if name == "vr20":
        return (keyword_cls("THINABA", ("1", f"{target:.2f}", "0.95", "0.0", "999.0", "0", "999")),)
    return (keyword_cls("THINBBA", ("1", f"{target:.2f}", "0.95", "0.0", "999.0", "0", "999")),)


def _keywords(
    *,
    au: int,
    treatment: str,
    residual_fraction: float | None,
    initial_ba: float,
    site_species: str,
    site_index: float,
    cycles: int = 10,
) -> tuple[Keyword, ...]:
    """Return the complete keyword set for one AU and treatment."""
    keyword_cls, _, _ = _require_fvsbc()
    title = f"AU{au} {treatment}"
    return (
        keyword_cls(
            "DATABASE",
            (),
            ("DSNOut", "FVSOut.db", "Summary", "TREELIDB", "CUTLIDB", "ComputDB"),
        ),
        keyword_cls("STDIDENT", (title,)),
        keyword_cls("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        keyword_cls("MANAGED", ("0", "1")),
        keyword_cls("SITECODE", (site_species, f"{site_index:.0f}")),
        keyword_cls("INVYEAR", ("0",)),
        keyword_cls("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        keyword_cls("NUMCYCLE", (str(cycles),)),
        keyword_cls("RANNSEED", ("1",)),
        keyword_cls("TREELIST", ("0",)),
        keyword_cls("CUTLIST", ("0",)),
        *_treatment_keywords(
            treatment,
            residual_fraction,
            initial_ba=initial_ba,
        ),
        keyword_cls("ECHOSUM"),
        keyword_cls("PROCESS"),
        keyword_cls("STOP"),
    )


def _read_table(
    database: Path,
    name: str,
) -> pd.DataFrame | None:
    """Read an optional FVS database table."""
    _, read_table, _ = _require_fvsbc()
    try:
        return read_table(database, name)
    except Exception:
        return None


def _run_one(
    *,
    au: int,
    treatment: str,
    residual_fraction: float | None,
    records: list[dict[str, float | int | str]],
    initial_ba: float,
    site_species: str,
    site_index: float,
    run_dir: Path,
    cycles: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Run one FVS-BC case and return summary, tree list, cut list, and metadata."""
    _, _, run_case = _require_fvsbc()
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    keywords = _keywords(
        au=au,
        treatment=treatment,
        residual_fraction=residual_fraction,
        initial_ba=initial_ba,
        site_species=site_species,
        site_index=site_index,
        cycles=cycles,
    )
    result: RunResult = run_case(records, keywords, directory=run_dir)
    summary = _read_table(result.database, "FVS_Summary_Metric")
    trees = _read_table(result.database, "FVS_TreeList_Metric")
    cuts = _read_table(result.database, "FVS_CutList_Metric")
    if summary is None or trees is None:
        raise RuntimeError(f"missing summary/tree table for AU {au} {treatment}")
    metadata: dict[str, object] = {
        "au": au,
        "treatment": treatment,
        "run_id": f"au{au:04d}_{treatment}",
        "case_id": result.provenance.case_id,
        "keyword_set_hash": result.provenance.keyword_set_hash,
        "treelist_hash": result.provenance.treelist_hash,
        "variant_list": result.provenance.variant_list,
        "warnings": result.warnings.to_dict("records"),
        "run_dir": str(run_dir),
    }
    return summary, trees, cuts if cuts is not None else pd.DataFrame(), metadata


def _tree_rows_for_au(
    *,
    au: int,
    tree_au: gpd.GeoDataFrame,
    au_row: pd.Series,
    seed: int,
) -> tuple[pd.DataFrame, dict[str, float], str, float]:
    """Return the sampled tree frame and species/age parameters for one AU."""
    joined = tree_au[tree_au["au"] == au]
    if joined.empty:
        raise ValueError(f"AU {au} has no 2009 trees")
    area_ha = float(au_row["area_ha"])
    target_tph = _target_tph(joined, area_ha)
    sample_size, expansion = _density_plan(target_tph)
    sample = _sample_rows(joined, sample_size)
    shares = {
        column.removeprefix("share_"): float(au_row[column])
        for column in au_row.index
        if str(column).startswith("share_")
    }
    species = _assign_species(shares, len(sample), seed=seed + au)
    age = float(au_row["age_2025"])
    site_species = _site_species(shares)
    site_index = SITE_INDEX.get(site_species, 90.0)
    records = _tree_records(sample, species, expansion=expansion, age=age)
    return (
        sample,
        {
            "area_ha": area_ha,
            "target_tph": target_tph,
            "sample_size": float(sample_size),
            "expansion": float(expansion),
            "age": age,
            "site_index": site_index,
            "initial_ba": _initial_ba(records),
        },
        site_species,
        age,
    )


def main() -> None:
    """Build the six-AU pilot and write combined evidence tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/fvsbc/gl_pilot"),
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=Path("ws4/runtime/fvsbc_gl_pilot/runs"),
    )
    parser.add_argument(
        "--psp-dir",
        type=Path,
        default=Path("../../inv01-data/psp"),
    )
    parser.add_argument("--all-aus", action="store_true")
    parser.add_argument("--aus", default=",".join(str(au) for au in PILOT_AUS))
    parser.add_argument(
        "--treatments",
        default=",".join(TREATMENTS),
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cycles", type=int, default=10)
    args = parser.parse_args()
    treatments = tuple(value.strip() for value in args.treatments.split(",") if value.strip())

    vri = gpd.read_file("data/inventory/gavin_vri_2025_start.gpkg")
    trees = gpd.read_file("data/lidar/gavin_2009/trees_filtered.gpkg")
    blocks = pd.read_parquet("ws4/runtime/legacy_matrix/blocks.parquet")
    tracks = pd.read_parquet("ws4/runtime/legacy_matrix/tracks.parquet")
    au_table = _au_table(vri, blocks, tracks)
    au_index = au_table.set_index("au")
    if args.all_aus:
        aus = tuple(
            int(value)
            for value in au_index.index
            if int(value) != 9999 and float(au_index.loc[value, "area_ha"]) > 0.0
        )
    else:
        aus = tuple(int(value) for value in args.aus.split(",") if value.strip())
    tree_au = _tree_au(trees, vri, blocks, tracks)
    psp_plots = _psp_plots(args.psp_dir) if args.psp_dir.exists() else pd.DataFrame()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.runs_dir.mkdir(parents=True, exist_ok=True)
    tree_lists_dir = args.out_dir / "tree_lists"
    tree_lists_dir.mkdir(parents=True, exist_ok=True)

    all_curves: list[pd.DataFrame] = []
    all_trees: list[pd.DataFrame] = []
    all_cuts: list[pd.DataFrame] = []
    all_runs: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    for au in aus:
        try:
            au_row = au_index.loc[au]
            sample, parameters, site_species, age = _tree_rows_for_au(
                au=au,
                tree_au=tree_au,
                au_row=au_row,
                seed=20261101,
            )
        except (KeyError, ValueError) as exc:
            print(f"skip AU {au}: {exc}", flush=True)
            skipped.append({"au": au, "reason": str(exc)})
            continue
        sample.to_csv(tree_lists_dir / f"au_{au:04d}_sample.csv", index=False)
        shares = au_row
        records_species = _assign_species(
            {
                column.removeprefix("share_"): float(shares[column])
                for column in shares.index
                if str(column).startswith("share_")
            },
            len(sample),
            seed=20261101 + au,
        )
        psp_ba, psp_age, psp_n = _psp_target(
            psp_plots,
            bec=str(shares["bec"]),
            age=age,
        )
        density_scale = (
            psp_ba / float(parameters["initial_ba"])
            if math.isfinite(psp_ba) and float(parameters["initial_ba"]) > 0.0
            else 1.0
        )
        scaled_expansion = max(1, round(float(parameters["expansion"]) * density_scale))
        records = _tree_records(
            sample,
            records_species,
            expansion=scaled_expansion,
            age=age,
        )
        initial_ba = _initial_ba(records)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(
                    _run_one,
                    au=au,
                    treatment=treatment,
                    residual_fraction=TREATMENTS[treatment],
                    records=records,
                    initial_ba=initial_ba,
                    site_species=site_species,
                    site_index=float(parameters["site_index"]),
                    run_dir=args.runs_dir / f"au_{au:04d}" / treatment,
                    cycles=args.cycles,
                ): treatment
                for treatment in treatments
            }
            for completed, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                treatment = futures[future]
                summary, tree_list, cuts, metadata = future.result()
                print(
                    f"AU {au} {treatment} ({completed}/{len(futures)})",
                    flush=True,
                )
                for frame, label in (
                    (summary, "summary"),
                    (tree_list, "trees"),
                    (cuts, "cuts"),
                ):
                    frame["au"] = au
                    frame["treatment"] = treatment
                    frame["run_id"] = metadata["run_id"]
                    frame["sample_size"] = int(parameters["sample_size"])
                    frame["expansion"] = int(parameters["expansion"])
                    frame["target_tph"] = float(parameters["target_tph"])
                    frame["area_ha"] = float(parameters["area_ha"])
                    frame["site_species"] = site_species
                    frame["site_index"] = float(parameters["site_index"])
                    frame["initial_ba_m2_ha"] = initial_ba
                    if label == "summary":
                        all_curves.append(frame)
                    elif label == "trees":
                        all_trees.append(frame)
                    else:
                        all_cuts.append(frame)
                metadata.update(
                    {
                        "area_ha": float(parameters["area_ha"]),
                        "target_tph": float(parameters["target_tph"]),
                        "sample_size": int(parameters["sample_size"]),
                        "expansion": int(parameters["expansion"]),
                        "initial_ba_m2_ha": initial_ba,
                        "psp_target_ba_m2_ha": psp_ba,
                        "psp_plots": psp_n,
                        "psp_age_bh": psp_age,
                        "density_scale": density_scale,
                        "scaled_expansion": scaled_expansion,
                        "site_species": site_species,
                        "site_index": float(parameters["site_index"]),
                        "tree_age": age,
                    }
                )
                all_runs.append(metadata)

    curves = pd.concat(all_curves, ignore_index=True)
    trees_out = pd.concat(all_trees, ignore_index=True)
    cuts_out = pd.concat(all_cuts, ignore_index=True) if all_cuts else pd.DataFrame()
    runs = pd.DataFrame(all_runs)
    curves.to_csv(args.out_dir / "curves.csv", index=False)
    trees_out.to_parquet(args.out_dir / "tree_trajectories.parquet", index=False)
    if not cuts_out.empty:
        cuts_out.to_parquet(args.out_dir / "cut_list.parquet", index=False)
    runs.to_csv(args.out_dir / "runs.csv", index=False)
    generated = datetime.now(UTC).isoformat()
    payload = {
        "generated_utc": generated,
        "source_tree_inventory": "data/lidar/gavin_2009/trees_filtered.gpkg",
        "source_vri": "data/inventory/gavin_vri_2025_start.gpkg",
        "aus": list(aus),
        "treatments": list(treatments),
        "runs": len(runs),
        "curves": len(curves),
        "tree_rows": len(trees_out),
        "cut_rows": len(cuts_out),
        "warnings": int(sum(len(value) for value in runs["warnings"] if isinstance(value, list))),
        "skipped": skipped,
        "scope": "all" if args.all_aus else "pilot",
        "psp_density_correction": bool(not psp_plots.empty),
        "caveats": [
            "2009 canopy inventory, not a CFI; species are assigned from VRI shares.",
            "DBH is height allometry; crown ratio is a fixed class 5.",
            "FVS-BC site index is a screening value, not a surveyed site index.",
            "FVS-BC basal-area thinning targets are metric m2/ha in this build.",
            "Tree counts are scaled to the Williams Lake PSP BEC/age BA analog; "
            "the LiDAR list supplies piece size.",
            "No regeneration, ingress, or planting is modelled in these runs.",
            (
                "All productive AUs are included; AU 9999 is excluded."
                if args.all_aus
                else "The six AUs are a pilot, not the full 80-AU estate."
            ),
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

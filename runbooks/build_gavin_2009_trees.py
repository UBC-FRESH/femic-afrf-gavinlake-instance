#!/usr/bin/env python3
"""Build a full Gavin Lake canopy-tree inventory from the 2009 FUSION LIDARBIN.

The 2009 `.las` files are valid FUSION LIDARBIN, not standard LAS. This runbook
uses the public-domain FUSION/LDV command-line tools under Wine:

- Catalog: identify the LIDARBIN tiles and extents;
- GridSurfaceCreate: build the bare-earth surface from the `gd` tiles;
- CanopyModel: normalize the `pt` point cloud and build a CHM;
- CanopyMaxima: detect canopy trees.

The result is a 2009 canopy inventory for the whole Gavin block. It is not a CFI:
species are unknown and DBH is a height-allometry estimate.

Usage::

    python runbooks/build_gavin_2009_trees.py \
      --las-dir external/.../LiDAR/2009 \
      --fusion-dir /tmp/opencode/fusion \
      --wineprefix /tmp/opencode/wine-fusion \
      --out-dir data/lidar/gavin_2009
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import contains_xy


def _wine(path: Path) -> str:
    """Return a Wine Z: path for a Linux path."""
    return "Z:" + str(path).replace("/", "\\")


def _run(command: list[str], wineprefix: Path) -> None:
    """Run a FUSION command under Wine."""
    subprocess.run(
        ["wine", *command],
        check=True,
        env={**dict(os.environ), "WINEPREFIX": str(wineprefix), "WINEDEBUG": "-all"},
        capture_output=True,
        text=True,
    )


def _catalog(
    pt_files: list[Path],
    fusion_dir: Path,
    wineprefix: Path,
    work_dir: Path,
) -> pd.DataFrame:
    """Catalog the pt tiles and return their bounds."""
    list_path = work_dir / "pt_list.txt"
    list_path.write_text("\n".join(_wine(path) for path in pt_files) + "\n")
    csv_base = work_dir / "pt_catalog"
    _run(
        [
            str(fusion_dir / "Catalog.exe"),
            "/quiet",
            "/nolaszipdll",
            _wine(list_path),
            _wine(csv_base),
        ],
        wineprefix,
    )
    return pd.read_csv(csv_base.with_suffix(".csv"))


def _tree_list(
    pt: Path,
    gd: Path,
    fusion_dir: Path,
    wineprefix: Path,
    tile_dir: Path,
) -> pd.DataFrame:
    """Build one tile's normalized CHM and return its tree list."""
    ground = tile_dir / "ground.dtm"
    chm = tile_dir / "chm.dtm"
    trees_base = tile_dir / "trees.csv"
    _run(
        [
            str(fusion_dir / "GridSurfaceCreate.exe"),
            "/minimum",
            _wine(ground),
            "1",
            "M",
            "M",
            "1",
            "10",
            "2",
            "0",
            _wine(gd),
        ],
        wineprefix,
    )
    _run(
        [
            str(fusion_dir / "canopymodel.exe"),
            f"/ground:{_wine(ground)}",
            _wine(chm),
            "1",
            "M",
            "M",
            "1",
            "10",
            "2",
            "0",
            _wine(pt),
        ],
        wineprefix,
    )
    _run(
        [
            str(fusion_dir / "CanopyMaxima.exe"),
            "/threshold:3",
            "/summary",
            _wine(chm),
            _wine(trees_base),
        ],
        wineprefix,
    )
    tree_list = tile_dir / "trees_treelist.csv"
    if not tree_list.exists():
        return pd.DataFrame()
    return pd.read_csv(tree_list)


def main() -> None:
    """Build and write the full Gavin 2009 tree inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--las-dir", type=Path, required=True)
    parser.add_argument("--fusion-dir", type=Path, required=True)
    parser.add_argument("--wineprefix", type=Path, required=True)
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/legacy_gavinlake/spatial/fragments.shp"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/lidar/gavin_2009"))
    parser.add_argument("--catalog", type=Path, help="Use an existing Catalog CSV.")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    blocks = gpd.read_file(args.blocks).to_crs(26910)
    union = blocks.geometry.union_all()
    work_dir = args.out_dir / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    pt_files = sorted(args.las_dir.glob("pt*.las"))
    if not pt_files:
        raise SystemExit("no pt*.las tiles found")
    if args.catalog:
        catalog = pd.read_csv(args.catalog)
    else:
        catalog = _catalog(pt_files, args.fusion_dir, args.wineprefix, work_dir)
    catalog["base"] = (
        catalog["FileName"].astype(str).str.replace("\\", "/", regex=False).str.split("/").str[-1]
    )
    selected = catalog[
        (catalog["MaxX"] >= union.bounds[0])
        & (catalog["MinX"] <= union.bounds[2])
        & (catalog["MaxY"] >= union.bounds[1])
        & (catalog["MinY"] <= union.bounds[3])
        & (catalog["base"].str.startswith("pt"))
    ]
    tasks: list[tuple[str, Path, Path, Path]] = []
    for record in selected.itertuples(index=False):
        name = str(record.base)
        pt = args.las_dir / name
        gd = args.las_dir / name.replace("pt", "gd", 1)
        if not gd.exists():
            continue
        tile_dir = work_dir / name.replace(".las", "")
        if tile_dir.exists():
            shutil.rmtree(tile_dir)
        tile_dir.mkdir(parents=True)
        tasks.append((name, pt, gd, tile_dir))

    def process(task: tuple[str, Path, Path, Path]) -> tuple[str, pd.DataFrame | None]:
        name, pt, gd, tile_dir = task
        try:
            trees = _tree_list(pt, gd, args.fusion_dir, args.wineprefix, tile_dir)
        except subprocess.CalledProcessError as exc:
            print(f"  {name} failed: {exc}", flush=True)
            return name, None
        if trees.empty:
            return name, None
        keep = contains_xy(union, trees["X"].to_numpy(), trees["Y"].to_numpy())
        return name, trees[keep].copy()

    rows: list[pd.DataFrame] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process, task): task[0] for task in tasks}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            name, trees = future.result()
            print(f"tile {completed}/{len(tasks)}: {name}", flush=True)
            if trees is not None and not trees.empty:
                rows.append(trees)

    if not rows:
        raise SystemExit("no trees detected")
    merged = pd.concat(rows, ignore_index=True)
    merged["tree_id"] = range(1, len(merged) + 1)
    merged["height_m"] = merged["Height"]
    merged["dbh_cm_est"] = np.exp(
        -0.015926556277605135 + 1.1004660678804368 * np.log(merged["height_m"].clip(lower=0.1))
    )
    trees = gpd.GeoDataFrame(
        merged,
        geometry=gpd.points_from_xy(merged["X"], merged["Y"]),
        crs=26910,
    ).to_crs(3005)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees.drop(columns="geometry").to_csv(args.out_dir / "trees.csv", index=False)
    trees.to_file(args.out_dir / "trees.gpkg", driver="GPKG")
    area_ha = float(blocks.geometry.area.sum() / 10_000.0)
    summary = {
        "source": "2009 FUSION LIDARBIN",
        "tiles": len(rows),
        "fragments": len(blocks),
        "area_ha": area_ha,
        "trees": len(trees),
        "tph": len(trees) / area_ha if area_ha else 0.0,
        "height_m": {
            "mean": float(trees["height_m"].mean()),
            "p50": float(trees["height_m"].median()),
            "p95": float(trees["height_m"].quantile(0.95)),
            "max": float(trees["height_m"].max()),
        },
        "dbh_cm_est": {
            "mean": float(trees["dbh_cm_est"].mean()),
            "p50": float(trees["dbh_cm_est"].median()),
            "max": float(trees["dbh_cm_est"].max()),
        },
        "method": "FUSION Catalog, GridSurfaceCreate, CanopyModel, CanopyMaxima",
        "calibration": "KC 2013 LAS calibration; threshold 3 m; default variable window",
        "caveats": [
            "Valid FUSION LIDARBIN, not corrupted LAS; converted/processed with FUSION.",
            "2009 canopy inventory, not a CFI.",
            "Species unknown; DBH is height allometry.",
            "Canopy maxima can split crowns.",
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

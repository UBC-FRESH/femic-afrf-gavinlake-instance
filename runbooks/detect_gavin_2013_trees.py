#!/usr/bin/env python3
"""Detect canopy trees in the 2013 LAS coverage over southern Gavin Lake.

The 2013 LAS tiles cover only about 448 ha of the Gavin Lake block. This runbook
applies the Knife Creek 2013 calibration (window 3, minimum height 3 m, NMS
radius 1.5 m) to those tiles, clips detections to the Gavin fragments, and writes
a partial tree-level inventory with a height-allometry DBH estimate.

Usage::

    python runbooks/detect_gavin_2013_trees.py \
      --las-dir external/.../LiDAR/2013 \
      --blocks data/legacy_gavinlake/spatial/fragments.shp \
      --out-dir data/lidar/gavin_2013
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import laspy
import numpy as np
import pandas as pd
from rasterio.transform import Affine
from scipy import ndimage
from shapely import contains_xy
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

WINDOW = 3
MIN_HEIGHT = 3.0
NMS_RADIUS = 1.5
ALLOMETRY_INTERCEPT = -0.015926556277605135
ALLOMETRY_SLOPE = 1.1004660678804368


def _canopy_grid(polygon: BaseGeometry, path: Path) -> tuple[np.ndarray, Affine]:
    """Build a 1 m canopy-height grid for one LAS tile and polygon."""
    minx, miny, maxx, maxy = polygon.bounds
    width = int(np.ceil(maxx - minx))
    height = int(np.ceil(maxy - miny))
    cloud = laspy.read(path)
    x = np.asarray(cloud.x)
    y = np.asarray(cloud.y)
    z = np.asarray(cloud.z)
    classification = np.asarray(cloud.classification)
    columns = np.floor(x - minx).astype(int)
    rows = np.floor(maxy - y).astype(int)
    valid = (columns >= 0) & (columns < width) & (rows >= 0) & (rows < height)
    rows, columns, z, classification = (
        rows[valid],
        columns[valid],
        z[valid],
        classification[valid],
    )
    if len(rows) == 0:
        return np.full((height, width), np.nan), Affine(1, 0, minx, 0, -1, maxy)
    flat = rows * width + columns
    order = np.argsort(flat, kind="stable")
    flat_sorted = flat[order]
    z_sorted = z[order]
    class_sorted = classification[order]
    unique, index = np.unique(flat_sorted, return_index=True)
    max_flat = np.full(height * width, -np.inf, dtype=float)
    min_flat = np.full(height * width, np.inf, dtype=float)
    max_flat[unique] = np.maximum.reduceat(z_sorted, index)
    min_flat[unique] = np.minimum.reduceat(z_sorted, index)
    ground_flat = np.full(height * width, np.inf, dtype=float)
    ground = class_sorted == 2
    if ground.any():
        ground_ids = flat_sorted[ground]
        ground_z = z_sorted[ground]
        ground_unique, ground_index = np.unique(ground_ids, return_index=True)
        ground_flat[ground_unique] = np.minimum.reduceat(ground_z, ground_index)
    max_grid = max_flat.reshape(height, width)
    min_grid = min_flat.reshape(height, width)
    ground_grid = ground_flat.reshape(height, width)
    ground_surface = np.where(np.isfinite(ground_grid), ground_grid, min_grid)
    with np.errstate(invalid="ignore"):
        canopy = max_grid - ground_surface
    canopy[~np.isfinite(canopy)] = np.nan
    return canopy, Affine(1, 0, minx, 0, -1, maxy)


def _detect_peaks(
    values: np.ndarray,
    transform: Affine,
    minimum_height: float,
    nms_radius_m: float,
) -> np.ndarray:
    """Return NMS-filtered local maxima in map coordinates."""
    valid = np.isfinite(values) & (values >= minimum_height) & (values < 80)
    peaks = (values == ndimage.maximum_filter(values, size=WINDOW)) & valid
    labels, count = ndimage.label(peaks, structure=np.ones((3, 3)))
    centers = ndimage.center_of_mass(peaks, labels, range(1, count + 1))
    candidates: list[tuple[float, float, float]] = []
    for row, column in centers:
        x, y = transform * (column + 0.5, row + 0.5)
        candidates.append((x, y, float(values[int(row), int(column)])))
    candidates.sort(key=lambda item: item[2], reverse=True)
    cell = max(nms_radius_m, 1e-6)
    grid: dict[tuple[int, int], list[tuple[float, float]]] = {}
    kept: list[tuple[float, float, float]] = []
    for x, y, height in candidates:
        cx, cy = int(x // cell), int(y // cell)
        keep = True
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for kx, ky in grid.get((cx + dx, cy + dy), []):
                    if (x - kx) ** 2 + (y - ky) ** 2 <= nms_radius_m**2:
                        keep = False
                        break
                if not keep:
                    break
            if not keep:
                break
        if keep:
            kept.append((x, y, height))
            grid.setdefault((cx, cy), []).append((x, y))
    return np.asarray([(x, y) for x, y, _ in kept], dtype=float)


def main() -> None:
    """Write the partial Gavin 2013 tree inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--las-dir", type=Path, required=True)
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/legacy_gavinlake/spatial/fragments.shp"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/lidar/gavin_2013"))
    args = parser.parse_args()

    blocks = gpd.read_file(args.blocks).to_crs(26910)
    union = blocks.geometry.union_all()
    rows: list[dict[str, object]] = []
    tiles = 0
    covered_area = 0.0
    for path in sorted(args.las_dir.glob("*.las")):
        with laspy.open(path) as reader:
            header = reader.header
            tile_bounds = (
                float(header.mins[0]),
                float(header.mins[1]),
                float(header.maxs[0]),
                float(header.maxs[1]),
            )
        if (
            tile_bounds[2] < union.bounds[0]
            or tile_bounds[0] > union.bounds[2]
            or tile_bounds[3] < union.bounds[1]
            or tile_bounds[1] > union.bounds[3]
        ):
            continue
        polygon = box(*tile_bounds).intersection(union)
        if polygon.is_empty:
            continue
        print(f"tile {path.name}: {polygon.area / 10000:.1f} ha", flush=True)
        canopy, transform = _canopy_grid(polygon, path)
        points = _detect_peaks(canopy, transform, MIN_HEIGHT, NMS_RADIUS)
        if len(points) == 0:
            continue
        keep = contains_xy(union, points[:, 0], points[:, 1])
        points = points[keep]
        print(f"  detected={len(points)}", flush=True)
        if len(points) == 0:
            continue
        for x, y in points:
            # Sample the canopy grid for the tree height.
            col = round((x - transform.c) / transform.a - 0.5)
            row = round((y - transform.f) / transform.e - 0.5)
            if row < 0 or col < 0 or row >= canopy.shape[0] or col >= canopy.shape[1]:
                continue
            height = float(canopy[row, col])
            if not np.isfinite(height):
                continue
            dbh = float(np.exp(ALLOMETRY_INTERCEPT + ALLOMETRY_SLOPE * np.log(height)))
            rows.append(
                {
                    "x": x,
                    "y": y,
                    "height_m": height,
                    "dbh_cm_est": dbh,
                    "species": "UNK",
                    "year": 2013,
                    "source_tile": path.name,
                    "source": "2013 LAS canopy maxima; KC calibration window 3, min 3 m, NMS 1.5 m",
                }
            )
        tiles += 1
        covered_area += float(polygon.area) / 10_000.0

    trees = gpd.GeoDataFrame(
        pd.DataFrame(rows),
        geometry=gpd.points_from_xy([row["x"] for row in rows], [row["y"] for row in rows]),
        crs=26910,
    ).to_crs(3005)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trees.drop(columns="geometry").to_csv(args.out_dir / "trees.csv", index=False)
    trees.to_file(args.out_dir / "trees.gpkg", driver="GPKG")

    area_ha = covered_area
    summary = {
        "tiles_processed": tiles,
        "fragments": len(blocks),
        "area_ha": area_ha,
        "trees": len(trees),
        "tph": len(trees) / area_ha if area_ha > 0 else 0.0,
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
        "calibration": {
            "window": WINDOW,
            "minimum_height_m": MIN_HEIGHT,
            "nms_radius_m": NMS_RADIUS,
            "source": "KC 2013 LAS calibration against Marshal tree maps, mean F1 0.656",
        },
        "caveats": [
            "Only the 2013 LAS tiles that intersect southern Gavin Lake are covered.",
            "The inventory is partial: about 448 ha of the 5,664 ha block.",
            "Species and understory are unknown; DBH is height allometry.",
            "Canopy maxima can split crowns; this is not a CFI.",
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a screening road-and-mill route network for Gavin Lake.

The public BC tenure-road layer is incomplete and disconnected. This runbook
turns it into a connected screening graph by:

- merging the public road sections into a line network;
- adding straight-line synthetic connectors between disconnected components;
- linking each split block to the nearest road vertex;
- linking a gateway vertex to the candidate sawlog mills; and
- writing the four route tables and a WS4 route configuration.

The cost rates are a named proxy from the TSA23 C5 route fixture, not AFRF
contract rates. The output is a screening delivered-wood layer, not an
operational or legal-access model.

Usage::

    python runbooks/build_gavin_screening_route.py \
      --out-dir data/delivered_wood/gavin/route
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist
from shapely.geometry import LineString
from shapely.ops import linemerge, unary_union

HAUL_RATE_PER_M3_M = 0.00016
BUILD_RATE_PER_M = 0.0
MAINTAIN_RATE_PER_M_YEAR = 2.0
MILL_ROAD_FACTOR = 1.25
PRODUCT_LABEL = "product.yield.managed.total"


def _line_parts(geom: object) -> list[LineString]:
    """Return the line parts of a Shapely line or multi-line geometry."""
    if geom.geom_type == "LineString":
        return [geom]
    if hasattr(geom, "geoms"):
        return [part for part in geom.geoms if part.geom_type == "LineString"]
    return []


def _component_labels(vertices: list[int], segments: list[dict[str, object]]) -> list[set[int]]:
    """Return connected components of a vertex/segment graph."""
    adjacency: dict[int, set[int]] = {vertex: set() for vertex in vertices}
    for segment in segments:
        start = int(segment["from_vertex"])
        end = int(segment["to_vertex"])
        adjacency[start].add(end)
        adjacency[end].add(start)
    seen: set[int] = set()
    components: list[set[int]] = []
    for vertex in vertices:
        if vertex in seen:
            continue
        stack = [vertex]
        seen.add(vertex)
        component: set[int] = set()
        while stack:
            current = stack.pop()
            component.add(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        components.append(component)
    return components


def main() -> None:
    """Build and write the screening route network."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blocks",
        type=Path,
        default=Path("data/legacy_gavinlake/spatial/fragments.shp"),
    )
    parser.add_argument(
        "--roads",
        type=Path,
        default=Path("data/roads/gavin_public_roads.gpkg"),
    )
    parser.add_argument(
        "--mills",
        type=Path,
        default=Path("data/mills/afrf_mill_candidates.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/delivered_wood/gavin/route"),
    )
    parser.add_argument("--max-mills", type=int, default=5)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    blocks = gpd.read_file(args.blocks).to_crs(3005)
    roads = gpd.read_file(args.roads).to_crs(3005)
    mills_all = pd.read_csv(args.mills)
    mills = (
        mills_all[
            (mills_all["product_code"] == "LBR")
            & (mills_all["status"] == "Op")
            & (mills_all["gavin_lake_km"] <= 100.0)
        ]
        .sort_values("gavin_lake_km")
        .head(args.max_mills)
        .copy()
    )
    if mills.empty:
        raise SystemExit("no candidate sawlog mills selected")

    merged = linemerge(unary_union(roads.geometry))
    lines = _line_parts(merged)

    vertices: dict[tuple[float, float], int] = {}
    vertex_rows: list[dict[str, object]] = []
    segments: list[dict[str, object]] = []
    next_vertex = 1
    next_segment = 1

    def vertex_id(coordinate: tuple[float, float]) -> int:
        nonlocal next_vertex
        key = (round(float(coordinate[0]), 1), round(float(coordinate[1]), 1))
        if key not in vertices:
            vertices[key] = next_vertex
            vertex_rows.append({"vertex_id": next_vertex, "x": key[0], "y": key[1]})
            next_vertex += 1
        return vertices[key]

    for line in lines:
        start = vertex_id(line.coords[0])
        end = vertex_id(line.coords[-1])
        if start == end:
            continue
        length = float(line.length)
        segments.append(
            {
                "segment_id": next_segment,
                "from_vertex": start,
                "to_vertex": end,
                "length_m": length,
                "haul_cost": length * HAUL_RATE_PER_M3_M,
                "build_cost": length * BUILD_RATE_PER_M,
                "maintain_cost": length * MAINTAIN_RATE_PER_M_YEAR,
                "road_class": "public_tenure",
                "source": "BC Forest Tenure Road Section Lines",
            }
        )
        next_segment += 1

    components = _component_labels([row["vertex_id"] for row in vertex_rows], segments)
    if len(components) > 1:
        representatives = []
        for component in components:
            representative = min(component)
            representatives.append(representative)
        coordinates = np.array(
            [
                [
                    next(row["x"] for row in vertex_rows if row["vertex_id"] == vertex),
                    next(row["y"] for row in vertex_rows if row["vertex_id"] == vertex),
                ]
                for vertex in representatives
            ]
        )
        distance = cdist(coordinates, coordinates)
        tree = minimum_spanning_tree(distance).toarray()
        for i, j in zip(*np.where(tree > 0), strict=True):
            length = float(distance[i, j])
            segments.append(
                {
                    "segment_id": next_segment,
                    "from_vertex": representatives[i],
                    "to_vertex": representatives[j],
                    "length_m": length,
                    "haul_cost": length * HAUL_RATE_PER_M3_M,
                    "build_cost": 0.0,
                    "maintain_cost": 0.0,
                    "road_class": "synthetic_component_connector",
                    "source": "screening assumption",
                }
            )
            next_segment += 1

    block_union = blocks.geometry.union_all()
    block_centroid = block_union.centroid
    vertex_coordinates = np.array([[row["x"], row["y"]] for row in vertex_rows], dtype=float)
    vertex_ids = np.array([row["vertex_id"] for row in vertex_rows], dtype=int)
    tree = cKDTree(vertex_coordinates)
    gateway_index = int(tree.query([block_centroid.x, block_centroid.y], k=1)[1])
    gateway_vertex = int(vertex_ids[gateway_index])

    linkages: list[dict[str, object]] = []
    access_distances: list[float] = []
    for _, block in blocks.iterrows():
        block_id = int(block["RES_KEY"])
        point = block.geometry.representative_point()
        distance, index = tree.query([point.x, point.y], k=1)
        road_vertex = int(vertex_ids[int(index)])
        block_vertex = int(1_000_000 + block_id)
        vertex_rows.append({"vertex_id": block_vertex, "x": float(point.x), "y": float(point.y)})
        segments.append(
            {
                "segment_id": next_segment,
                "from_vertex": block_vertex,
                "to_vertex": road_vertex,
                "length_m": float(distance),
                "haul_cost": float(distance) * HAUL_RATE_PER_M3_M,
                "build_cost": 0.0,
                "maintain_cost": 0.0,
                "road_class": "block_access_screening",
                "source": "nearest public-road vertex; screening assumption",
            }
        )
        next_segment += 1
        linkages.append(
            {
                "block_id": block_id,
                "vertex_id": block_vertex,
                "link_distance_m": float(distance),
            }
        )
        access_distances.append(float(distance))

    destinations: list[dict[str, object]] = []
    mill_rows: list[dict[str, object]] = []
    for index, mill in mills.reset_index(drop=True).iterrows():
        mill_vertex = int(2_000_000 + index)
        mill_point = (
            gpd.GeoSeries(
                [gpd.points_from_xy([mill["longitude"]], [mill["latitude"]])[0]],
                crs=4326,
            )
            .to_crs(3005)
            .iloc[0]
        )
        straight = float(mill_point.distance(block_centroid))
        length = straight * MILL_ROAD_FACTOR
        vertex_rows.append(
            {
                "vertex_id": mill_vertex,
                "x": float(mill_point.x),
                "y": float(mill_point.y),
            }
        )
        segments.append(
            {
                "segment_id": next_segment,
                "from_vertex": gateway_vertex,
                "to_vertex": mill_vertex,
                "length_m": length,
                "haul_cost": length * HAUL_RATE_PER_M3_M,
                "build_cost": 0.0,
                "maintain_cost": 0.0,
                "road_class": "synthetic_mill_connector",
                "source": "straight-line distance x 1.25; screening assumption",
            }
        )
        next_segment += 1
        destinations.append({"name": mill["destination"], "vertex_id": mill_vertex})
        mill_rows.append(
            {
                "destination": mill["destination"],
                "company": mill["company"],
                "locality": mill["locality"],
                "product_code": mill["product_code"],
                "capacity_value": mill["capacity_value"],
                "capacity_unit": mill["capacity_unit"],
                "status": mill["status"],
                "gavin_lake_km": mill["gavin_lake_km"],
                "synthetic_route_km": length / 1000.0,
            }
        )

    pd.DataFrame(vertex_rows).to_csv(args.out_dir / "vertices.csv", index=False)
    pd.DataFrame(segments).to_csv(args.out_dir / "segments.csv", index=False)
    pd.DataFrame(destinations).to_csv(args.out_dir / "destinations.csv", index=False)
    pd.DataFrame(linkages).to_csv(args.out_dir / "linkages.csv", index=False)
    pd.DataFrame(mill_rows).to_csv(args.out_dir / "mills_selected.csv", index=False)

    eligibility = pd.DataFrame(
        [{"product": PRODUCT_LABEL, "destination": row["name"]} for row in destinations]
    )
    eligibility.to_csv(args.out_dir / "eligibility.csv", index=False)

    route_config = {
        "route": {
            "segments": "segments.csv",
            "vertices": "vertices.csv",
            "destinations": "destinations.csv",
            "linkages": "linkages.csv",
            "eligibility": "eligibility.csv",
            "initial_roads": "all",
        },
        "route_accounts": [
            {
                "destination": row["name"],
                "kind": "haul",
                "account": f"route.{row['name']}.haul",
            }
            for row in destinations
        ]
        + [
            {
                "destination": row["name"],
                "kind": "volume",
                "account": f"product.{row['name']}.Yield",
            }
            for row in destinations
        ],
        "duplicate_accounts": [
            {
                "master": f"route.{row['name']}.haul",
                "target": "route.Total.haul",
            }
            for row in destinations
        ],
    }
    (args.out_dir / "route.yaml").write_text(yaml.safe_dump(route_config, sort_keys=False))

    metadata = {
        "purpose": "screening delivered-wood route network for Gavin Lake",
        "blocks": len(blocks),
        "public_road_segments": len(lines),
        "component_count_before_connectors": len(components),
        "synthetic_component_connectors": max(0, len(components) - 1),
        "mills": mill_rows,
        "rates": {
            "haul_cad_per_m3_m": HAUL_RATE_PER_M3_M,
            "build_cad_per_m": BUILD_RATE_PER_M,
            "maintain_cad_per_m_year": MAINTAIN_RATE_PER_M_YEAR,
            "mill_road_factor": MILL_ROAD_FACTOR,
            "basis": "TSA23 C5 route fixture medians; screening proxy, not AFRF contract rates",
        },
        "access_distance_m": {
            "min": float(np.min(access_distances)),
            "median": float(np.median(access_distances)),
            "p90": float(np.percentile(access_distances, 90)),
            "max": float(np.max(access_distances)),
        },
        "caveats": [
            "Public tenure-road layer is incomplete: 19.3 km against 112.2 km in MWP #3 Table 37.",
            "Disconnected public-road components are joined by straight synthetic connectors.",
            "Block access is a straight line to the nearest public-road vertex.",
            "Mill haul is a straight-line distance times 1.25, not a routed highway path.",
            "Rates are TSA23 proxies, not AFRF contract rates.",
            "This is a screening layer, not a legal access or operational model.",
        ],
    }
    (args.out_dir / "route_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(
        f"blocks={len(blocks)} segments={len(segments)} mills={len(destinations)} "
        f"components={len(components)}"
    )


if __name__ == "__main__":
    main()

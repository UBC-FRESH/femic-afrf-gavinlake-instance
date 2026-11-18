#!/usr/bin/env python3
"""Derive Gavin Lake MDWR habitat classes from the official BC map.

The 2007 AFRF Management and Working Plan #3 says the Beaver Valley MDWR
habitat classes are depicted in Appendix 9, with the class boundaries adjusted
to the research forest's total-chance harvest blocks.  The public BC map used
here is the underlying long-term habitat objective map for Beaver Valley North
(Prouton Lakes), dated 6 December 2001.

This script extracts the High/Moderate/Low habitat polygons from that PDF,
georeferences them from the printed UTM grid, and assigns each MDWR block a
class by largest intersected area.  It is a data-preparation step, not a legal
determination.  In particular, it does not claim that the fine polygons are the
adjusted Appendix 9 compartment boundaries.

Outputs:
  * block-level CSV with class areas and a model-class field;
  * clipped class polygons as GeoJSON;
  * a JSON manifest recording the source hash and georeference constants.

Run from the Gavin Lake instance root with the public PDF path supplied:

    python scripts/build_mdwr_official_habitat.py \
        --pdf /path/to/beavervly_lto.pdf \
        --out-prefix planning/2026-11-18_gavin_mdwr_official_habitat
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pymupdf
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[1]
SPATIAL = ROOT / "data" / "legacy_gavinlake" / "spatial" / "fragments.shp"

# PDF-point frame read from the printed 4 km UTM grid on the map.
PDF_LEFT = 210.71875
PDF_RIGHT = 1931.261719
PDF_TOP = 270.378906
PDF_BOTTOM = 1908.121094
UTM_LEFT = 560000.0
UTM_RIGHT = 592000.0
UTM_TOP = 5836000.0
UTM_BOTTOM = 5808000.0
SCENE_CRS = "EPSG:3005"
MAP_CRS = "EPSG:26910"

CLASS_COLORS = {
    "High": (0.0, 0.661, 0.615),
    "Moderate": (0.539, 0.765, 0.252),
    "Low": (0.607, 0.811, 0.670),
}
BEC_PROXY = {
    "ICHmk3": "High",
    "ICHmk3/SBSdw": "Moderate",
    "SBSdw1": "Low",
}
COVERAGE_FLOOR = 0.50


def _is_color(fill: tuple[float, float, float] | None, target: tuple[float, float, float]) -> bool:
    """Return whether a PDF fill colour matches a map class colour."""
    return fill is not None and max(abs(fill[i] - target[i]) for i in range(3)) < 0.01


def _pdf_to_utm(x: float, y: float) -> tuple[float, float]:
    """Map PDF page points to UTM zone 10N using the printed grid frame."""
    easting = UTM_LEFT + (x - PDF_LEFT) * (UTM_RIGHT - UTM_LEFT) / (PDF_RIGHT - PDF_LEFT)
    northing = UTM_TOP - (y - PDF_TOP) * (UTM_TOP - UTM_BOTTOM) / (PDF_BOTTOM - PDF_TOP)
    return easting, northing


def _to_albers(geometry: object) -> object:
    """Reproject a PDF-point geometry to BC Albers through UTM zone 10N."""
    utm = transform(_pdf_to_utm, geometry)
    to_albers = Transformer.from_crs(MAP_CRS, SCENE_CRS, always_xy=True)
    return transform(lambda x, y, z=None: to_albers.transform(x, y), utm)


def _drawing_polygon(items: list[tuple[object, ...]]) -> Polygon | None:
    """Build a polygon from PyMuPDF path items, ignoring unsupported curves."""
    points: list[tuple[float, float]] = []
    for item in items:
        kind = item[0]
        if kind == "l":
            points.extend([(item[1].x, item[1].y), (item[2].x, item[2].y)])
        elif kind == "c":
            points.extend([(item[1].x, item[1].y), (item[4].x, item[4].y)])
        elif kind == "re":
            rect = item[1]
            points.extend(
                [
                    (rect.x0, rect.y0),
                    (rect.x1, rect.y0),
                    (rect.x1, rect.y1),
                    (rect.x0, rect.y1),
                ]
            )
    if len(points) < 4:
        return None
    polygon = Polygon(points)
    if not polygon.is_valid or polygon.area <= 0.01:
        return None
    return polygon


def extract_classes(pdf_path: Path) -> dict[str, object]:
    """Extract and georeference the three habitat-class polygon unions."""
    document = pymupdf.open(pdf_path)
    page = document[0]
    polygons: dict[str, list[Polygon]] = {name: [] for name in CLASS_COLORS}
    for drawing in page.get_drawings(extended=True):
        rect = drawing.get("rect")
        if rect is None:
            continue
        if rect.x0 < 200 or rect.x1 > 2000 or rect.y0 < 250 or rect.y1 > 1950:
            continue
        for name, color in CLASS_COLORS.items():
            if not _is_color(drawing.get("fill"), color):
                continue
            polygon = _drawing_polygon(drawing["items"])
            if polygon is not None:
                polygons[name].append(polygon)
            break
    if any(not values for values in polygons.values()):
        missing = [name for name, values in polygons.items() if not values]
        raise RuntimeError(f"no polygons extracted for classes: {missing}")
    return {
        name: _to_albers(unary_union(values))
        for name, values in polygons.items()
    }


def block_table(class_geometries: dict[str, object]) -> pd.DataFrame:
    """Assign each MDWR block a class from largest intersected class area."""
    frame = gpd.read_file(SPATIAL)
    mdwr = frame.loc[frame["WORKING_CI"] == "MDWR"].copy()
    rows: list[dict[str, object]] = []
    for row in mdwr.itertuples(index=False):
        geometry = row.geometry
        area_ha = float(geometry.area) / 10000.0
        parts = {
            name: float(geometry.intersection(class_geometries[name]).area) / 10000.0
            for name in class_geometries
        }
        official_ha = sum(parts.values())
        official_class = max(parts, key=parts.get) if official_ha > 0 else "Unclassified"
        coverage = official_ha / area_ha if area_ha > 0 else 0.0
        bec = str(row.BEC)
        model_class = (
            official_class
            if coverage >= COVERAGE_FLOOR and official_class != "Unclassified"
            else BEC_PROXY.get(bec, "Low")
        )
        rows.append(
            {
                "block_id": int(row.RES_KEY),
                "area_ha": round(area_ha, 6),
                "bec": bec,
                "high_ha": round(parts["High"], 6),
                "moderate_ha": round(parts["Moderate"], 6),
                "low_ha": round(parts["Low"], 6),
                "official_ha": round(official_ha, 6),
                "coverage": round(coverage, 6),
                "official_class": official_class,
                "model_class": model_class,
                "class_basis": "official" if model_class == official_class else "bec_fallback",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument(
        "--out-prefix",
        type=Path,
        default=ROOT / "planning" / "2026-11-18_gavin_mdwr_official_habitat",
    )
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    classes = extract_classes(pdf_path)
    table = block_table(classes)
    out_prefix = args.out_prefix
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_prefix.with_suffix(".csv")
    geo_path = out_prefix.with_suffix(".geojson")
    manifest_path = out_prefix.with_suffix(".json")
    table.to_csv(csv_path, index=False)

    source = gpd.read_file(SPATIAL)
    mdwr_union = source.loc[source["WORKING_CI"] == "MDWR"].geometry.union_all()
    clipped = []
    for name, geometry in classes.items():
        clipped.append({"class": name, "geometry": geometry.intersection(mdwr_union)})
    class_frame = gpd.GeoDataFrame(clipped, crs=SCENE_CRS)
    class_frame.to_file(geo_path, driver="GeoJSON")

    manifest = {
        "source_pdf": pdf_path.name,
        "source_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "source_url": (
            "https://www.env.gov.bc.ca/cariboo/env_stewardship/ecosystems/"
            "mdwr_strat/maps/beavervly_lto.pdf"
        ),
        "map_title": "Long-Term Habitat Objectives: Beaver Valley North (Prouton Lakes)",
        "map_date": "2001-12-06",
        "map_appendix": "Appendix 11",
        "georeference": {
            "pdf_points": [PDF_LEFT, PDF_RIGHT, PDF_TOP, PDF_BOTTOM],
            "utm_zone": "10N",
            "utm_extent": [UTM_LEFT, UTM_RIGHT, UTM_BOTTOM, UTM_TOP],
            "target_crs": SCENE_CRS,
            "method": "printed 4 km grid frame; separate x/y affine scaling",
        },
        "coverage_floor": COVERAGE_FLOOR,
        "bec_proxy": BEC_PROXY,
        "caveat": (
            "The 2007 MWP #3 Appendix 9 map is a compartment-level adjusted "
            "representation. This table uses the public BC long-term objective "
            "polygons, not the adjusted compartment boundaries; it is a "
            "screening input, not a legal determination."
        ),
        "class_area_in_mdwr_ha": {
            name: round(
                float(table[f"{name.lower()}_ha"].sum()),
                3,
            )
            for name in ("High", "Moderate", "Low")
        },
        "block_counts": table["model_class"].value_counts().to_dict(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {csv_path} ({len(table)} blocks)")
    print(f"wrote {geo_path} ({len(class_frame)} class geometries)")
    print(f"wrote {manifest_path}")
    print(table.groupby("model_class")[["area_ha"]].sum().round(1).to_string())


if __name__ == "__main__":
    main()

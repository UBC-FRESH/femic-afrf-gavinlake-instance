#!/usr/bin/env python3
"""Build planted bare-ground regeneration curves for the Gavin Lake AUs.

Each AU gets one FVS-BC bare-ground case with a planted species and site index.
The summary is converted from the BC imperial report to metric trees per hectare,
basal area, merchantable volume, and top height.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

FT3_PER_ACRE_TO_M3_PER_HA = 0.028316846592 / 0.40468564224
FT2_PER_ACRE_TO_M2_PER_HA = 0.09290304 / 0.40468564224


def _key_text(*, au: int, species: str, site_index: float) -> str:
    """Return the raw FVS-BC key for a planted bare-ground case."""
    return f"""STDIDENT
AU{au} planted regeneration
STDINFO   712       CHS131    0         200       35        16
MANAGED   0         1
SITECODE  {species:<10}{site_index:<10.0f}
INVYEAR   0
DESIGN    0         1         999       1         0         1         1
NUMCYCLE  10
RANNSEED  1
NOTREES
ESTAB
PLANT     1         {species:<10}450       95        2         1         0
END
ECHOSUM
PROCESS
STOP
"""


def _run_au(*, au: int, species: str, site_index: float) -> pd.DataFrame:
    """Run one bare-ground case and return its metric summary."""
    from pyfvs import fvs

    with tempfile.TemporaryDirectory(prefix=f"regen_au{au}_") as directory:
        key = Path(directory) / "regen.key"
        key.write_text(_key_text(au=au, species=species, site_index=site_index))
        model = fvs.FVS("bc")
        model.init_projection(str(key))
        for _ in range(model.globals.ncyc):
            model.grow()
        model.end_projection()
        summary = model.summary.copy()
    summary["Year"] = summary["year"].astype(int)
    summary["TPH"] = summary["tpa"].astype(float) * 2.471053814671653
    summary["BA_m2_ha"] = summary["baa"].astype(float) * FT2_PER_ACRE_TO_M2_PER_HA
    summary["MCuM"] = summary["mcuft"].astype(float) * FT3_PER_ACRE_TO_M3_PER_HA
    summary["TopHt_m"] = summary["top_ht"].astype(float) * 0.3048
    summary["au"] = au
    summary["species"] = species
    summary["site_index"] = site_index
    return summary[["au", "species", "site_index", "Year", "TPH", "BA_m2_ha", "MCuM", "TopHt_m"]]


def main() -> None:
    """Write the regeneration curve library."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        type=Path,
        default=Path("data/fvsbc/gl_all/runs.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/fvsbc/gl_regen"),
    )
    parser.add_argument("--aus", default="")
    args = parser.parse_args()
    runs = pd.read_csv(args.runs).drop_duplicates("au")
    if args.aus:
        selected = {int(value) for value in args.aus.split(",") if value.strip()}
        runs = runs[runs["au"].isin(selected)]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    metadata: list[dict[str, object]] = []
    for row in runs.sort_values("au").itertuples(index=False):
        au = int(row.au)
        species = str(row.site_species)
        site_index = float(row.site_index)
        print(f"AU {au} planted {species} SI {site_index:.0f}", flush=True)
        try:
            summary = _run_au(au=au, species=species, site_index=site_index)
        except Exception as exc:
            print(f"  failed: {exc}", flush=True)
            metadata.append({"au": au, "species": species, "status": "failed", "error": str(exc)})
            continue
        frames.append(summary)
        metadata.append(
            {
                "au": au,
                "species": species,
                "site_index": site_index,
                "status": "ok",
                "max_year": int(summary["Year"].max()),
                "final_m3_ha": float(
                    summary.loc[summary["Year"] == summary["Year"].max(), "MCuM"].iloc[0]
                ),
            }
        )
    curves = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    curves.to_csv(args.out_dir / "regen_curves.csv", index=False)
    pd.DataFrame(metadata).to_csv(args.out_dir / "regen_runs.csv", index=False)
    payload = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "aus": len(metadata),
        "ok": sum(1 for row in metadata if row["status"] == "ok"),
        "curves": len(curves),
        "caveats": [
            "Bare-ground planted stand; not a measured regeneration survey.",
            "One species per AU, site index from the AU FVS run.",
            "No natural ingress, brushing, or competition control.",
        ],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

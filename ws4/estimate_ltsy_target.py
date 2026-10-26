#!/usr/bin/env python3
"""Estimate a first-guess periodic harvest target from the compiled matrix.

The method is the one used for a blind LTSY estimate:

1. build an area-weighted mean yield curve from the current track curves;
2. find the culmination of mean annual increment (CMAI);
3. multiply CMAI by the THLB area to get a long-term sustained yield (LTSY);
4. multiply by the period width; and
5. multiply by an uplift (default 1.1) for a slightly-too-high first guess.

The THLB proxy is the productive forest class ``CONTCLAS = C``. The estimator
also reports an all-area sensitivity. It is a first guess, not an AAC
determination.

Run from the instance root:

    python ws4/estimate_ltsy_target.py \
      --dataset ws4/runtime/legacy_matrix \
      --fragments data/legacy_gavinlake/fragments.csv \
      --out ws4/evidence/ltsy/estimate.json \
      --curve-csv ws4/evidence/ltsy/mean_yield_curve.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATASET = Path("ws4/runtime/legacy_matrix")
DEFAULT_FRAGMENTS = Path("data/legacy_gavinlake/fragments.csv")
DEFAULT_OUT = Path("ws4/evidence/ltsy/estimate.json")
DEFAULT_CURVE_CSV = Path("ws4/evidence/ltsy/mean_yield_curve.csv")
DEFAULT_LABEL = "feature.yield.managed.total"
DEFAULT_THLB_CLASS = "C"
DEFAULT_PERIOD_WIDTH = 10
DEFAULT_UPLIFT = 1.1
DEFAULT_MAX_AGE = 300


def interp_value(xs: np.ndarray, ys: np.ndarray, age: float) -> float:
    """Return a linear interpolation of a curve at an age.

    Parameters
    ----------
    xs : numpy.ndarray
        Strictly increasing x values.
    ys : numpy.ndarray
        y values aligned with ``xs``.
    age : float
        The age to evaluate.

    Returns
    -------
    float
        The interpolated value, clamped to the curve's endpoints.
    """
    if xs.size == 0:
        return 0.0
    if age <= xs[0]:
        return float(ys[0])
    if age >= xs[-1]:
        return float(ys[-1])
    upper = int(np.searchsorted(xs, age, side="right"))
    x0, x1 = float(xs[upper - 1]), float(xs[upper])
    y0, y1 = float(ys[upper - 1]), float(ys[upper])
    if x1 == x0:
        return y1
    return y0 + (y1 - y0) * (age - x0) / (x1 - x0)


def curve_table(curves: pd.DataFrame) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Index the curve table by curve id.

    Parameters
    ----------
    curves : pandas.DataFrame
        The ws4 ``curves`` table with ``curve_id``, ``x``, and ``y``.

    Returns
    -------
    dict of int to tuple of (numpy.ndarray, numpy.ndarray)
        Each curve's sorted x and y arrays.
    """
    table: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for curve_id, frame in curves.groupby("curve_id", sort=False):
        ordered = frame.sort_values("x")
        table[int(curve_id)] = (
            ordered["x"].to_numpy(dtype=float),
            ordered["y"].to_numpy(dtype=float),
        )
    return table


def feature_curve_ids(features: pd.DataFrame, label: str) -> dict[int, int]:
    """Map a track to its feature curve for one label.

    Parameters
    ----------
    features : pandas.DataFrame
        The ws4 ``features`` table.
    label : str
        The feature label, such as ``feature.yield.managed.total``.

    Returns
    -------
    dict of int to int
        Track id to curve id.
    """
    selected = features.loc[features["label"] == label, ["track_id", "curve_id"]]
    return {
        int(row.track_id): int(row.curve_id)
        for row in selected.drop_duplicates().itertuples(index=False)
    }


def mean_yield_curve(
    *,
    fragments: pd.DataFrame,
    curve_ids: dict[int, int],
    curves: dict[int, tuple[np.ndarray, np.ndarray]],
    max_age: int,
) -> pd.DataFrame:
    """Build the area-weighted mean yield curve and its mean annual increment.

    Parameters
    ----------
    fragments : pandas.DataFrame
        The derived fragment table with ``TRACK`` and ``AREA_HA``.
    curve_ids : dict of int to int
        Track id to feature curve id.
    curves : dict of int to tuple of (numpy.ndarray, numpy.ndarray)
        Curve id to sorted x and y arrays.
    max_age : int
        The last age to evaluate, in years.

    Returns
    -------
    pandas.DataFrame
        Columns ``age``, ``mean_yield_m3_ha``, and ``mai_m3_ha_yr``.
    """
    ages = np.arange(1, max_age + 1)
    area = fragments["AREA_HA"].to_numpy(dtype=float)
    total_area = float(area.sum())
    if total_area <= 0.0:
        raise ValueError("fragment area is zero")
    mean_yield = np.zeros(ages.size, dtype=float)
    for index, age in enumerate(ages):
        values = np.array(
            [
                interp_value(*curves[curve_ids[int(track)]], float(age))
                if int(track) in curve_ids
                else 0.0
                for track in fragments["TRACK"].to_numpy()
            ],
            dtype=float,
        )
        mean_yield[index] = float(np.sum(area * values) / total_area)
    return pd.DataFrame(
        {
            "age": ages,
            "mean_yield_m3_ha": mean_yield,
            "mai_m3_ha_yr": mean_yield / ages,
        }
    )


def ltsy_from_curve(
    curve: pd.DataFrame, *, area_ha: float, period_width: int, uplift: float
) -> dict[str, float | int]:
    """Return the CMAI and LTSY first-guess target from a mean yield curve.

    Parameters
    ----------
    curve : pandas.DataFrame
        The mean yield curve from :func:`mean_yield_curve`.
    area_ha : float
        The THLB area in hectares.
    period_width : int
        The accounting period width, in years.
    uplift : float
        The multiplier for a slightly-too-high first guess.

    Returns
    -------
    dict of str to float or int
        CMAI, CMAI age, LTSY, and the periodic first guess.
    """
    best = curve.loc[curve["mai_m3_ha_yr"].idxmax()]
    cmai = float(best["mai_m3_ha_yr"])
    cmai_age = int(best["age"])
    annual = cmai * area_ha
    period = annual * period_width
    return {
        "cmai_m3_ha_yr": round(cmai, 6),
        "cmai_age_years": cmai_age,
        "mean_yield_at_cmai_m3_ha": round(float(best["mean_yield_m3_ha"]), 6),
        "ltsy_annual_m3": round(annual, 2),
        "ltsy_period_m3": round(period, 2),
        "period_width_years": period_width,
        "uplift": uplift,
        "first_guess_period_target_m3": round(period * uplift, 2),
        "first_guess_period_target_rounded_m3": int(round(period * uplift, -3)),
    }


def estimate(
    *,
    dataset: Path,
    fragments_path: Path,
    label: str = DEFAULT_LABEL,
    thlb_class: str = DEFAULT_THLB_CLASS,
    period_width: int = DEFAULT_PERIOD_WIDTH,
    uplift: float = DEFAULT_UPLIFT,
    max_age: int = DEFAULT_MAX_AGE,
) -> tuple[dict[str, object], pd.DataFrame]:
    """Estimate the LTSY first-guess target.

    Parameters
    ----------
    dataset : Path
        The ws4 dataset directory.
    fragments_path : Path
        The derived fragment table with ``CONTCLAS``, ``TRACK``, and ``AREA_HA``.
    label : str, optional
        The feature yield label. The default is
        ``feature.yield.managed.total``.
    thlb_class : str, optional
        The productive ``CONTCLAS`` value. The default is ``C``.
    period_width : int, optional
        The accounting period width. The default is 10.
    uplift : float, optional
        The first-guess uplift. The default is 1.1.
    max_age : int, optional
        The last age to evaluate. The default is 300.

    Returns
    -------
    tuple of (dict of str to object, pandas.DataFrame)
        The estimate and the THLB mean yield curve.
    """
    from ws4.model.api import Model

    model = Model.from_dataset(dataset)
    curves = curve_table(model.table("curves"))
    curve_ids = feature_curve_ids(model.table("features"), label)
    fragments = pd.read_csv(fragments_path)

    thlb = fragments.loc[fragments["CONTCLAS"] == thlb_class].copy()
    if thlb.empty:
        raise ValueError(f"no fragments with CONTCLAS={thlb_class!r}")
    thlb_curve = mean_yield_curve(
        fragments=thlb, curve_ids=curve_ids, curves=curves, max_age=max_age
    )
    thlb_estimate = ltsy_from_curve(
        thlb_curve,
        area_ha=float(thlb["AREA_HA"].sum()),
        period_width=period_width,
        uplift=uplift,
    )

    all_curve = mean_yield_curve(
        fragments=fragments, curve_ids=curve_ids, curves=curves, max_age=max_age
    )
    all_estimate = ltsy_from_curve(
        all_curve,
        area_ha=float(fragments["AREA_HA"].sum()),
        period_width=period_width,
        uplift=uplift,
    )

    result: dict[str, object] = {
        "dataset": str(dataset),
        "fragments": str(fragments_path),
        "label": label,
        "thlb_definition": f"CONTCLAS={thlb_class}",
        "thlb_area_ha": round(float(thlb["AREA_HA"].sum()), 6),
        "max_age_years": max_age,
        **thlb_estimate,
        "all_area_sensitivity": {
            "area_ha": round(float(fragments["AREA_HA"].sum()), 6),
            **all_estimate,
        },
    }
    return result, thlb_curve


def main() -> None:
    """Run the LTSY estimator from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--fragments", type=Path, default=DEFAULT_FRAGMENTS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--curve-csv", type=Path, default=DEFAULT_CURVE_CSV)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--thlb-class", default=DEFAULT_THLB_CLASS)
    parser.add_argument("--period-width", type=int, default=DEFAULT_PERIOD_WIDTH)
    parser.add_argument("--uplift", type=float, default=DEFAULT_UPLIFT)
    parser.add_argument("--max-age", type=int, default=DEFAULT_MAX_AGE)
    args = parser.parse_args()

    estimate_result, curve = estimate(
        dataset=args.dataset,
        fragments_path=args.fragments,
        label=args.label,
        thlb_class=args.thlb_class,
        period_width=args.period_width,
        uplift=args.uplift,
        max_age=args.max_age,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(estimate_result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.curve_csv.parent.mkdir(parents=True, exist_ok=True)
    curve.to_csv(args.curve_csv, index=False)
    print(json.dumps(estimate_result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

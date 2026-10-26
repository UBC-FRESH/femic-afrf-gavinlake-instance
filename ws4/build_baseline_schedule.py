#!/usr/bin/env python3
"""Build a reproducible sustained-yield baseline schedule for the Gavin Lake matrix.

The baseline is a heuristic, not an optimization. It schedules the legacy
clearcut treatment at the minimum operable age (80 years) and then re-enters
each block every 80 years, up to the horizon. The first entry is assigned to a
ten-year period to spread the estimated harvest volume as evenly as possible.

The schedule is written as ``block_id,treatment,offset``. The estimate JSON
records the volume the heuristic expected; the simulation is the authority.

Run from the instance root:

    python ws4/build_baseline_schedule.py \
      --dataset ws4/runtime/legacy_matrix \
      --out ws4/schedules/baseline_evenflow.csv \
      --estimate ws4/evidence/baseline/estimate.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATASET = Path("ws4/runtime/legacy_matrix")
DEFAULT_OUT = Path("ws4/schedules/baseline_evenflow.csv")
DEFAULT_ESTIMATE = Path("ws4/evidence/baseline/estimate.json")
DEFAULT_YEARS = 300
DEFAULT_PERIOD_WIDTH = 10
DEFAULT_MIN_AGE = 80
DEFAULT_TREATMENT = "CC"
DEFAULT_LABEL = "product.yield.managed.total"


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


def product_curves(products: pd.DataFrame, treatment: str, label: str) -> dict[int, int]:
    """Map a track to its product curve for one treatment and label.

    Parameters
    ----------
    products : pandas.DataFrame
        The ws4 ``products`` table.
    treatment : str
        The treatment name, such as ``CC``.
    label : str
        The product label, such as ``product.yield.managed.total``.

    Returns
    -------
    dict of int to int
        Track id to curve id.
    """
    selected = products.loc[(products["treatment"] == treatment) & (products["label"] == label)]
    return {int(row.track_id): int(row.curve_id) for row in selected.itertuples(index=False)}


def transitions(treatments: pd.DataFrame, treatment: str) -> dict[int, tuple[int, int, int]]:
    """Map a track to its treatment transition.

    Parameters
    ----------
    treatments : pandas.DataFrame
        The ws4 ``treatments`` table.
    treatment : str
        The treatment name, such as ``CC``.

    Returns
    -------
    dict of int to tuple of (int, int, int)
        Track id to ``(new_track, begin_age, end_age)``.
    """
    selected = treatments.loc[treatments["treatment"] == treatment]
    return {
        int(row.track_id): (int(row.new_track), int(row.begin), int(row.end))
        for row in selected.itertuples(index=False)
    }


def entry_chain(
    *,
    track_id: int,
    age0: int,
    first_offset: int,
    area_ha: float,
    years: int,
    min_age: int,
    treatment: str,
    product_curve_ids: dict[int, int],
    transition_map: dict[int, tuple[int, int, int]],
    curves: dict[int, tuple[np.ndarray, np.ndarray]],
) -> list[tuple[int, float]]:
    """Return the treatment offsets and estimated volumes for one block.

    Parameters
    ----------
    track_id : int
        The block's initial track.
    age0 : int
        The block's initial age.
    first_offset : int
        The first treatment offset, in years after the simulation start.
    area_ha : float
        The block's area.
    years : int
        The simulation horizon.
    min_age : int
        The minimum operable age.
    treatment : str
        The treatment name.
    product_curve_ids : dict of int to int
        Track to product curve id.
    transition_map : dict of int to tuple of (int, int, int)
        Track to ``(new_track, begin_age, end_age)``.
    curves : dict of int to tuple of (numpy.ndarray, numpy.ndarray)
        Curve id to sorted x and y arrays.

    Returns
    -------
    list of tuple of (int, float)
        ``(offset, estimated_volume_m3)`` for each entry.
    """
    entries: list[tuple[int, float]] = []
    track = track_id
    offset = first_offset
    age = age0 + first_offset
    while offset < years:
        curve_id = product_curve_ids.get(track)
        volume = 0.0
        if curve_id is not None:
            xs, ys = curves.get(curve_id, (np.array([]), np.array([])))
            volume = area_ha * interp_value(xs, ys, float(age))
        entries.append((offset, volume))
        transition = transition_map.get(track)
        if transition is None:
            break
        new_track, begin, end = transition
        if age < begin or age > end:
            break
        track = new_track
        offset += min_age
        age = min_age
    return entries


def block_profiles(
    *,
    fragments: pd.DataFrame,
    years: int,
    period_width: int,
    min_age: int,
    treatment: str,
    product_curve_ids: dict[int, int],
    transition_map: dict[int, tuple[int, int, int]],
    curves: dict[int, tuple[np.ndarray, np.ndarray]],
) -> dict[int, dict[int, list[float]]]:
    """Return the candidate first-period profiles for every block.

    Parameters
    ----------
    fragments : pandas.DataFrame
        The ws4 ``fragments`` table.
    years : int
        The simulation horizon.
    period_width : int
        The accounting period width, in years.
    min_age : int
        The minimum operable age.
    treatment : str
        The treatment name.
    product_curve_ids : dict of int to int
        Track to product curve id.
    transition_map : dict of int to tuple of (int, int, int)
        Track to ``(new_track, begin_age, end_age)``.
    curves : dict of int to tuple of (numpy.ndarray, numpy.ndarray)
        Curve id to sorted x and y arrays.

    Returns
    -------
    dict of int to dict of int to list of float
        Block id to candidate first period to per-period estimated volume.
    """
    periods = years // period_width
    profiles: dict[int, dict[int, list[float]]] = {}
    for row in fragments.itertuples(index=False):
        block_id = int(row.block_id)
        age0 = int(row.age)
        area = float(row.area_ha)
        track = int(row.track_id)
        earliest = max(0, min_age - age0)
        if earliest >= years:
            continue
        first_period = earliest // period_width
        candidates: dict[int, list[float]] = {}
        for period in range(first_period, periods):
            offset = max(earliest, period * period_width)
            if offset >= years:
                continue
            entries = entry_chain(
                track_id=track,
                age0=age0,
                first_offset=offset,
                area_ha=area,
                years=years,
                min_age=min_age,
                treatment=treatment,
                product_curve_ids=product_curve_ids,
                transition_map=transition_map,
                curves=curves,
            )
            profile = [0.0] * periods
            for entry_offset, volume in entries:
                profile[entry_offset // period_width] += volume
            candidates[period] = profile
        if candidates:
            profiles[block_id] = candidates
    return profiles


def choose_first_periods(
    *,
    fragments: pd.DataFrame,
    profiles: dict[int, dict[int, list[float]]],
    years: int,
    period_width: int,
) -> dict[int, int]:
    """Choose a first period for every block by greedy load balancing.

    Parameters
    ----------
    fragments : pandas.DataFrame
        The ws4 ``fragments`` table.
    profiles : dict of int to dict of int to list of float
        Candidate profiles from :func:`block_profiles`.
    years : int
        The simulation horizon.
    period_width : int
        The accounting period width.

    Returns
    -------
    dict of int to int
        Block id to chosen first period.
    """
    periods = years // period_width
    totals = [0.0] * periods
    for candidates in profiles.values():
        earliest = min(candidates)
        for index, value in enumerate(candidates[earliest]):
            totals[index] += value
    target = sum(totals) / periods if periods else 0.0

    totals = [0.0] * periods
    chosen: dict[int, int] = {}
    age_by_block = {int(row.block_id): int(row.age) for row in fragments.itertuples(index=False)}
    for block_id in sorted(profiles, key=lambda key: (age_by_block[key], key)):
        candidates = profiles[block_id]
        best_period = min(candidates)
        best_cost: float | None = None
        for period, add in candidates.items():
            cost = 0.0
            for index, value in enumerate(add):
                if value:
                    before = totals[index] - target
                    after = before + value
                    cost += after * after - before * before
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_period = period
        chosen[block_id] = best_period
        for index, value in enumerate(candidates[best_period]):
            totals[index] += value
    return chosen


def build_schedule(
    *,
    dataset: Path,
    years: int = DEFAULT_YEARS,
    period_width: int = DEFAULT_PERIOD_WIDTH,
    min_age: int = DEFAULT_MIN_AGE,
    treatment: str = DEFAULT_TREATMENT,
    label: str = DEFAULT_LABEL,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Build the sustained-yield baseline schedule and its estimate.

    Parameters
    ----------
    dataset : Path
        The ws4 dataset directory.
    years : int, optional
        The simulation horizon. The default is 300.
    period_width : int, optional
        The accounting period width. The default is 10.
    min_age : int, optional
        The minimum operable age. The default is 80.
    treatment : str, optional
        The treatment name. The default is ``CC``.
    label : str, optional
        The product label. The default is ``product.yield.managed.total``.

    Returns
    -------
    tuple of (pandas.DataFrame, dict of str to object)
        The schedule and the estimate summary.
    """
    from ws4.model.api import Model

    model = Model.from_dataset(dataset)
    fragments = model.table("fragments")
    products = model.table("products")
    treatments = model.table("treatments")
    curves = curve_table(model.table("curves"))

    product_curve_ids = product_curves(products, treatment, label)
    transition_map = transitions(treatments, treatment)
    profiles = block_profiles(
        fragments=fragments,
        years=years,
        period_width=period_width,
        min_age=min_age,
        treatment=treatment,
        product_curve_ids=product_curve_ids,
        transition_map=transition_map,
        curves=curves,
    )
    chosen = choose_first_periods(
        fragments=fragments,
        profiles=profiles,
        years=years,
        period_width=period_width,
    )

    periods = years // period_width
    totals = [0.0] * periods
    rows: list[dict[str, object]] = []
    for row in fragments.itertuples(index=False):
        block_id = int(row.block_id)
        period = chosen.get(block_id)
        if period is None:
            continue
        earliest = max(0, min_age - int(row.age))
        first_offset = max(earliest, period * period_width)
        entries = entry_chain(
            track_id=int(row.track_id),
            age0=int(row.age),
            first_offset=first_offset,
            area_ha=float(row.area_ha),
            years=years,
            min_age=min_age,
            treatment=treatment,
            product_curve_ids=product_curve_ids,
            transition_map=transition_map,
            curves=curves,
        )
        for offset, volume in entries:
            rows.append({"block_id": block_id, "treatment": treatment, "offset": offset})
            totals[offset // period_width] += volume

    schedule = pd.DataFrame(rows, columns=["block_id", "treatment", "offset"])
    schedule = schedule.sort_values(["offset", "block_id"]).reset_index(drop=True)
    estimate: dict[str, object] = {
        "dataset": str(dataset),
        "years": years,
        "period_width": period_width,
        "min_age": min_age,
        "treatment": treatment,
        "label": label,
        "fragments": len(fragments),
        "scheduled_blocks": len(chosen),
        "schedule_rows": len(schedule),
        "estimated_volume_by_period_m3": [round(value, 2) for value in totals],
        "estimated_total_m3": round(sum(totals), 2),
        "estimated_mean_m3": round(sum(totals) / periods, 2) if periods else 0.0,
        "estimated_min_m3": round(min(totals), 2) if totals else 0.0,
        "estimated_max_m3": round(max(totals), 2) if totals else 0.0,
    }
    return schedule, estimate


def main() -> None:
    """Run the baseline builder from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--estimate", type=Path, default=DEFAULT_ESTIMATE)
    parser.add_argument("--years", type=int, default=DEFAULT_YEARS)
    parser.add_argument("--period-width", type=int, default=DEFAULT_PERIOD_WIDTH)
    parser.add_argument("--min-age", type=int, default=DEFAULT_MIN_AGE)
    parser.add_argument("--treatment", default=DEFAULT_TREATMENT)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    args = parser.parse_args()

    schedule, estimate = build_schedule(
        dataset=args.dataset,
        years=args.years,
        period_width=args.period_width,
        min_age=args.min_age,
        treatment=args.treatment,
        label=args.label,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    schedule.to_csv(args.out, index=False)
    args.estimate.parent.mkdir(parents=True, exist_ok=True)
    args.estimate.write_text(
        json.dumps(estimate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(estimate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

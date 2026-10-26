# Gavin Lake baseline findings

Date: 2026-10-26
Phase: P1
Status: evidence recorded, phase closeout pending

## Baseline definition

The baseline is a reproducible sustained-yield schedule built by
`ws4/build_baseline_schedule.py`:

- clearcut (`CC`) at the minimum operable age of 80 years;
- re-enter the block every 80 years, up to the 300-year horizon;
- assign first entries to ten-year periods with a greedy volume-balancing
  heuristic; and
- do not enforce spatial or patch targets.

The schedule is `ws4/schedules/baseline_evenflow.csv` (10,113 rows, 2,907
blocks). The heuristic estimate is `ws4/evidence/baseline/estimate.json`.

## Simulated result

The simulation matches the heuristic estimate almost exactly.

| Metric | Value |
| --- | --- |
| Mean harvest per ten-year period | 188,677.89 m³ |
| Minimum period harvest | 177,070.07 m³ |
| Maximum period harvest | 197,806.62 m³ |
| Total harvest over 300 years | 5,660,336.77 m³ |
| Initial growing stock | 1,418,962.31 m³ |
| Growing stock at year 300 | 495,510.56 m³ |

Harvest by decade is in `ws4/evidence/baseline/summary.json`. The profile is
flat in absolute volume, between about 177,000 and 198,000 m³ per decade.

## Comparison with the legacy targets

| Legacy target | Legacy value | Baseline result | Status |
| --- | --- | --- | --- |
| Harvest floor, each period | 500,000 m³ | 177,070–197,807 m³ | below |
| Growing stock at period 30 | 1,277,067 m³ | 495,511 m³ | below |
| Even-flow band, periods 1–30 | −1 to 1 percent | about 0–11 percent above the final period | above |

The target report has 31 `below`, 26 `above`, and 4 `met` rows. See
`ws4/evidence/baseline/target_report.csv`.

## Interpretation

The compiled H matrix has one treatment: clearcut at age 80 or more. A
sustained 80-year rotation on the 4,663 ha productive area produces about
189,000 m³ per decade. The legacy 500,000 m³ floor would require roughly 2.6
times that sustained yield. The one-time pulse of every age-80-plus block
produces about 1.26 million m³ in the first decade, so the floor is reachable
once, but not sustained.

The growing-stock floor and the harvest floor pull in opposite directions. The
baseline harvests enough to reduce growing stock to about 496,000 m³ at year
300; meeting the 1,277,067 m³ floor would require a much lighter harvest.

The even-flow target is expressed as a percentage of the final period. A
profile that is flat in absolute volume is not flat in that ratio when the
final period is lower than the mean. The baseline is therefore even in
absolute terms but outside the legacy −1 to 1 percent band.

## What would change the conclusion

- A different volume unit or landbase in the legacy model. The compiled matrix
  is the authority here; the original XML/workbook would settle it.
- A treatment other than clearcut at 80. The compiled matrix has no partial
  cutting, retention, or selection treatment.
- A different growth curve or yield adjustment. The baseline uses the compiled
  `product.yield.managed.total` curves as they are.
- A longer rotation or a lower harvest target. Both would raise ending growing
  stock and lower periodic harvest.

## Evidence

- `ws4/schedules/baseline_evenflow.csv`
- `ws4/evidence/baseline/estimate.json`
- `ws4/evidence/baseline/summary.json`
- `ws4/evidence/baseline/target_report.csv`
- `ws4/evidence/baseline/ending_inventory.csv`
- `ws4/schedules/smoke_age80_pulse.csv` and
  `ws4/evidence/smoke_age80/summary.json` for the one-time pulse comparison

## What is not claimed

- This is not an optimized schedule.
- This is not a historical solver replay; the archive has no populated
  scenario outputs.
- The carbon scenarios are not evaluated.
- The baseline does not enforce spatial, patch, or road constraints.

# Gavin Lake baseline findings

Date: 2026-10-26
Phase: P1
Status: evidence recorded, phase closeout approved

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

## Comparison with the scenario targets

| Scenario target | Value | Baseline result | Status |
| --- | --- | --- | --- |
| Harvest floor, each period | 500,000 m³ | 177,070–197,807 m³ | below |
| Growing stock at period 30 | 1,277,067 m³ | 495,511 m³ | below |
| Even-flow band, periods 1–30 | −1 to 1 percent | about 0–11 percent above the final period | above |

The target report has 31 `below`, 26 `above`, and 4 `met` rows. See
`ws4/evidence/baseline/target_report.csv`.

## LTSY comparison

The LTSY first guess is derived in `ws4/evidence/ltsy/estimate.json`:

| Item | Value |
| --- | --- |
| THLB proxy (`CONTCLAS = C`) | 4,662.96 ha |
| Area-weighted mean yield CMAI | 3.599653 m³/ha/yr |
| CMAI age | 100 years |
| LTSY annual | 16,785.06 m³/yr |
| LTSY per ten-year period | 167,850.57 m³ |
| ×1.1 first guess | 184,635.63 m³ |
| Rounded target | 185,000 m³ |

The baseline mean of 188,677.89 m³ is about 2.2 percent above the LTSY ×1.1
first guess. The baseline meets the 185,000 m³ target in 22 of 30 periods; the
eight misses are 177,070–184,810 m³. That is a reasonable first-guess target:
close enough to be useful, slightly above LTSY, and not a fabricated policy
floor.

The 500,000 m³ literal is about 2.7 times the LTSY ×1.1 first guess. It remains
useful as a parity reference and as a possible pull-up target, but it is not a
sensible first-guess harvest level for this matrix.

The all-area sensitivity is 5,663.66 ha, CMAI 3.532573 m³/ha/yr, LTSY
20,007.31 m³/yr, and a ×1.1 first guess of 220,080.41 m³ per period. The THLB
proxy is the primary result.

## Target interpretation

The 500,000 m³ harvest floor is a literal in the legacy scenario script. The
archive does not record the modeler's intent. In Patchworks, an unattainable
minimum with a linear penalty is a legitimate pull-up technique, especially
when paired with an even-flow target on the same harvest account. The AFRF
scenario sets `setLinear(true)` on the harvest target and then activates an
even-flow target on `product.flow.yield.even`, so a pull-up interpretation is
consistent with the script.

It is not proven. The value could also be a calibrated floor, a template value,
or an exploratory setting. That is a question for the modeler.

The 1,277,067 m³ growing-stock floor is consistent with 90 percent of the
measured initial growing stock (1,418,962.31 m³), as the script comment says.
Whether it is a hard policy floor or a scenario choice is also the modeler's
call.

## Interpretation of the baseline

The baseline sustains about 189,000 m³ per decade under an 80-year clearcut
rotation. It does not reach 500,000 m³ per decade. That is a factual result
about this schedule and this matrix.

If the 500,000 is a pull-up target, the shortfall is expected and is not a
finding about policy feasibility. If it is intended as a feasible floor, then
the matrix, treatment set, landbase, or units need reconciliation. The archive
does not settle which case applies.

The baseline is flat in absolute volume. The even-flow target is expressed as a
percentage of the final period, so a flat absolute profile is not flat in that
ratio. The target report records the deviations.

## What would change the interpretation

- A recorded statement of the 500,000 target's intent.
- A different volume unit or landbase in the legacy model.
- A treatment other than clearcut at 80. The compiled matrix has no partial
  cutting, retention, or selection treatment.
- A different growth curve or yield adjustment.
- A longer rotation or a lower harvest target.

## Evidence

- `notes/reference/legacy-target-provenance.md`
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
- The baseline shortfall is not a verdict on the 500,000 target's intent or on
  an AFRF policy.

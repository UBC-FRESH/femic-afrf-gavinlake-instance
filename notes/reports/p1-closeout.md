# Phase 1 close-out report

Phase identifier: P1
Status: approved and merged in pull request #13
Branch: `feature/p1-scenario-baseline`
Parent issue: #7

## Goal

Translate the legacy H scenario catalog into a ws4 target contract and build a
reproducible baseline schedule that can be compared with the legacy matrix
behaviour.

## What was done

- Recorded all nine legacy scenarios in `ws4/scenarios/legacy_catalog.yaml` and
  documented their disposition.
- Translated `scenario_01` (timber harvest) into
  `ws4/targets_legacy_harvest.yaml`.
- Deferred the eight carbon scenarios with a specific reason: the compiled
  matrix does not carry the runtime duplicate stock/flux accounts and the
  target units are unresolved.
- Built `ws4/build_baseline_schedule.py`, a reproducible sustained-yield
  baseline builder.
- Generated `ws4/schedules/baseline_evenflow.csv` (10,113 rows, 2,907 blocks).
- Simulated the baseline for 300 years with the legacy topology and patch
  accounts.
- Ran the translated target report and recorded the result.
- Wrote `notes/reference/gavin-baseline-findings.md`.

## Evidence

- `ws4/scenarios/legacy_catalog.yaml`
- `ws4/scenarios/README.md`
- `ws4/targets_legacy_harvest.yaml`
- `ws4/build_baseline_schedule.py`
- `ws4/schedules/baseline_evenflow.csv`
- `ws4/evidence/baseline/estimate.json`
- `ws4/evidence/baseline/summary.json`
- `ws4/evidence/baseline/target_report.csv`
- `ws4/evidence/baseline/ending_inventory.csv`
- `notes/reference/gavin-baseline-findings.md`

## Findings

- The baseline mean harvest is 188,677.89 m³ per ten-year period, with a
  minimum of 177,070.07 and a maximum of 197,806.62 m³.
- The 500,000 m³ period target is not met. The archive does not record the
  modeler's intent for that value. In Patchworks, an unattainable minimum with
  a linear penalty can be a deliberate pull-up technique, especially when
  paired with an even-flow target. The shortfall is therefore not a verdict on
  the target or on an AFRF policy.
- The 1,277,067 m³ growing-stock target is not met; the baseline ends at
  495,510.56 m³. The target is consistent with 90 percent of the measured
  initial growing stock, as the script comment says.
- The baseline is flat in absolute volume but not within the −1 to 1 percent
  even-flow band when each period is compared with the final period.
- The one-time age-80 pulse produces about 1.26 million m³ in the first decade
  and then no sustained harvest.

## Post-closeout correction

The first version of this report inferred that the 500,000 was a copied
template value and treated the baseline shortfall as evidence of
infeasibility. That overreached. The value is a scenario parameter; its intent
is the modeler's and is not recorded in the archive. The scenario's linear
penalty on `product.yield.managed.total` and its even-flow target on
`product.flow.yield.even` are consistent with a deliberate pull-up target. The
record now separates the factual baseline result from the intent question. See
`notes/reference/legacy-target-provenance.md`.

## LTSY first-guess addendum

After the Phase 1 closeout, `ws4/estimate_ltsy_target.py` was added to derive a
defensible first-guess periodic harvest target:

- THLB proxy (`CONTCLAS = C`): 4,662.96 ha;
- area-weighted mean yield CMAI: 3.599653 m³/ha/yr at age 100;
- LTSY: 16,785.06 m³/yr, or 167,850.57 m³ per ten-year period;
- ×1.1 first guess: 184,635.63 m³, rounded to 185,000.

The baseline mean of 188,677.89 m³ is about 2.2 percent above the first guess,
and the baseline meets 185,000 m³ in 22 of 30 periods. The eight misses are
177,070–184,810 m³. The 1,277,067 m³ growing-stock target remains the binding
constraint.

The runnable target is `ws4/targets_gavin_ltsy.yaml`. The literal 500,000
remains in `ws4/targets_legacy_harvest.yaml` as a parity reference. The LTSY
estimate is in `ws4/evidence/ltsy/`.

## What is not done

- No optimization run.
- No carbon scenario evaluation.
- No spatial, patch, road, or silvicultural treatment beyond clearcut at 80.
- No canonical FEMIC rebuild.

## Risks

- The legacy target units and landbase may differ from the compiled matrix.
- The baseline's greedy period assignment is a heuristic, not a yield
  calculation; the simulation is the authority.
- The carbon deferral is a real gap, not a claim that the carbon scenarios are
  unimportant.

## Recommendation

Approve Phase 1 and proceed to Phase 2 (ws4 runtime packaging) or Phase 3
(verification and QA). Do not treat the baseline as an optimized result.

Use `ws4/targets_gavin_ltsy.yaml` as the first runnable target. Keep the
literal 500,000 in `ws4/targets_legacy_harvest.yaml` as a parity reference. If
the 500,000 is a deliberate pull-up target, report the trajectory and penalties
as such; if it is intended as a feasible floor, reconcile the landbase, units,
and treatment set with the legacy source first.

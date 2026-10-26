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
- The copied legacy 500,000 m³ per period template floor is not feasible on
  this matrix under the only available treatment, clearcut at age 80 or more.
- The legacy 1,277,067 m³ growing-stock floor at period 30 is not met; the
  baseline ends at 495,510.56 m³.
- The baseline is flat in absolute volume but not within the legacy −1 to 1
  percent even-flow band when each period is compared with the final period.
- The one-time age-80 pulse produces about 1.26 million m³ in the first decade
  and then no sustained harvest.

## Post-closeout correction

The 500,000 m³ harvest floor was initially described as a legacy target. It is
a copied MKRF legacy template value, not an AFRF-calibrated target. The AFRF
package's build scripts still point at `PW_MKRF`, and the same literal appears
in the MKRF `Targets/01_harvest.bsh`. The 1,277,067 m³ growing-stock floor is
calibrated to this matrix (90 percent of initial growing stock) and remains the
primary structural benchmark. See
`notes/reference/legacy-target-provenance.md`.

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
(verification and QA). Do not treat the baseline as an optimized result. If a
500,000 m³ floor is confirmed as a real policy target, the next step is to
reconcile the landbase, units, and treatment set with the legacy source before
optimizing.

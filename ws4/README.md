# Gavin Lake ws4 runtime

The ws4 runtime is built from the legacy H matrix by ingestion:

```bash
ws4 ingest \
  --matrix data/legacy_gavinlake/tracks/H \
  --fragments data/legacy_gavinlake/fragments.csv \
  --out ws4/runtime/legacy_matrix
ws4 validate --dataset ws4/runtime/legacy_matrix
```

The ingest maps the legacy matrix tables to the ws4 schema. The source hashes
are in the dataset manifest.

## Translation table

| Legacy surface | ws4 surface |
| --- | --- |
| `tracks/H/blocks.csv` | `blocks` |
| `tracks/H/curves.csv` | `curves` |
| `tracks/H/features.csv` | `features` |
| `tracks/H/products.csv` | `products` |
| `tracks/H/accounts.csv` | `accounts` |
| `tracks/H/protoaccounts.csv` | `protoaccounts` |
| `tracks/H/strata.csv` | `strata` |
| `tracks/H/tracknames.csv` | `tracks` |
| `tracks/H/treatments.csv` | `treatments` |
| `tracks/H/groups.csv` | `groups` |
| `tracks/H/messages.csv` | `messages` |
| `spatial/fragments.shp` + `blocks.csv` | `fragments` via `fragments.csv` |
| `spatial/topo_fragments.csv` | `topology.csv` |

## Targets and accounts

`targets_legacy_harvest.yaml` translates the legacy timber-harvest scenario:

- 500,000 m³ per 10-year period for 30 periods (copied MKRF template value;
  parity reference, not an AFRF-calibrated target);
- 1,277,067 m³ growing stock at period 30; and
- an even-flow band of -1 to 1, weight 1000.

`patch_accounts.yaml` translates the legacy patch accounts:

- `patch.grpblk` on `product.area.managed.total`, 20 m topology, five size
  classes; and
- `patch.sepblk` on `feature.area.managed.seral.le10`, 100 m topology, three
  size classes.

The legacy scenarios do not set patch share targets. These are reporting
accounts, not an opening-size policy.

## Scenario catalog

`ws4/scenarios/legacy_catalog.yaml` records all nine legacy scenarios and their
translation status. Only `scenario_01` (maximize timber harvest) is translated
into a ws4 target file. The eight carbon scenarios are deferred because the
compiled matrix does not carry the runtime duplicate stock/flux accounts and
the target units are unresolved. See `ws4/scenarios/README.md`.

## Baseline schedule

`ws4/schedules/baseline_evenflow.csv` is a reproducible sustained-yield
baseline. It clearcuts at the minimum operable age (80 years), re-enters every
80 years, and assigns first entries to ten-year periods by a greedy
volume-balancing heuristic. It does not enforce spatial or patch targets.

Build it from the compiled dataset:

```bash
python ws4/build_baseline_schedule.py \
  --dataset ws4/runtime/legacy_matrix \
  --out ws4/schedules/baseline_evenflow.csv \
  --estimate ws4/evidence/baseline/estimate.json
```

Run it:

```bash
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/baseline_evenflow.csv \
  --years 300 \
  --out ws4/runtime/baseline_evenflow \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
ws4 report \
  --run ws4/runtime/baseline_evenflow \
  --targets ws4/targets_legacy_harvest.yaml \
  --out ws4/runtime/baseline_evenflow_report
```

The result is a mean harvest of 188,677.89 m³ per ten-year period, a minimum of
177,070.07, and a maximum of 197,806.62 m³. The copied legacy 500,000 m³ template floor is not feasible on this matrix
under the only available treatment. It is a parity reference, not an
AFRF-calibrated target; see `../notes/reference/legacy-target-provenance.md`. The growing stock
falls from 1,418,962.31 m³ to 495,510.56 m³ over 300 years, so the legacy
1,277,067 m³ floor at period 30 is also not met.

## Smoke run

`ws4/schedules/smoke_age80_pulse.csv` assigns one `CC` treatment at offset 0 to
every fragment aged 80 or more. It is a structural check, not a policy
baseline. The run:

```bash
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/smoke_age80_pulse.csv \
  --years 300 \
  --out ws4/runtime/smoke_age80 \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
```

## Evidence

- `evidence/legacy_ingest.json` — counts, area, age handling, and the
  initial-growing-stock parity check.
- `evidence/baseline/estimate.json` — the heuristic's expected volume by
  period.
- `evidence/baseline/summary.json` — the simulated baseline result, the legacy
  target values, and the target-status counts.
- `evidence/baseline/target_report.csv` — one row per translated target.
- `evidence/baseline/ending_inventory.csv` — the ending inventory report.
- `evidence/smoke_age80/summary.json` — harvest by decade, selected growing
  stock values, and the patch summary at offset 0.

## Boundaries

- The archive has no ForestModelXML, so this is an ingest, not a recipe
  rebuild.
- The archive has no populated scenario outputs, so there is no like-for-like
  historical result.
- The smoke run does not meet the translated targets. It exists to prove the
  dataset and the account machinery run.
- Generated runtime files stay under `ws4/runtime/` and are ignored by Git.

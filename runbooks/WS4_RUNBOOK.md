# Gavin Lake ws4 runbook

## Build

```bash
ws4 ingest \
  --matrix data/legacy_gavinlake/tracks/H \
  --fragments data/legacy_gavinlake/fragments.csv \
  --out ws4/runtime/legacy_matrix
ws4 validate --dataset ws4/runtime/legacy_matrix
```

## Simulate the smoke schedule

```bash
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/smoke_age80_pulse.csv \
  --years 300 \
  --out ws4/runtime/smoke_age80 \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
```

## Report against the translated targets

```bash
ws4 report \
  --run ws4/runtime/smoke_age80 \
  --targets ws4/targets_legacy_harvest.yaml \
  --out ws4/runtime/smoke_age80_report
```

The smoke run will violate the targets by design. Use the report to confirm
that the target reader and the account names line up.

## Optimize

The legacy targets are in `ws4/targets_legacy_harvest.yaml`. An optimization
run is deferred to Phase 1 because the project needs a reviewed baseline
schedule first.

## Evidence

- `ws4/evidence/legacy_ingest.json`
- `ws4/evidence/smoke_age80/summary.json`

## Outputs

`ws4/runtime/` is ignored. If a run becomes public evidence, add a short JSON
summary under `ws4/evidence/` and update `CHANGE_LOG.md`.

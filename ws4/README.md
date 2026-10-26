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

- 500,000 m³ per 10-year period for 30 periods;
- 1,277,067 m³ growing stock at period 30; and
- an even-flow band of -1 to 1, weight 1000.

`patch_accounts.yaml` translates the legacy patch accounts:

- `patch.grpblk` on `product.area.managed.total`, 20 m topology, five size
  classes; and
- `patch.sepblk` on `feature.area.managed.seral.le10`, 100 m topology, three
  size classes.

The legacy scenarios do not set patch share targets. These are reporting
accounts, not an opening-size policy.

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

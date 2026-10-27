# AFRF Gavin Lake Instance

A **ws4 forest-estate model instance** for the Gavin Lake block of the UBC Alex
Fraser Research Forest (AFRF). It translates a legacy Patchworks matrix into a
ws4-native compiled dataset, keeps the legacy package as a benchmark reference,
and records the structural parity evidence.

## Status

Phase 0 (bootstrap, legacy intake, and structural parity) is complete. The
legacy H matrix has been ingested and validated by ws4, and the initial growing
stock reproduces the value implied by the legacy scenario constraints. Phase 1
(scenario translation and baseline benchmark) is complete; its P1.6 public
benchmark addendum is in review. Phase 2 (ws4 runtime packaging) is active on a
separate branch. See `ROADMAP.md` for the phase and task plan, and
`CHANGE_LOG.md` for the dated record.

## What this repository contains

- `data/legacy_gavinlake/` — the sanitized legacy AFRF H matrix, the spatial
  inventory, the proximal topology, and the legacy scenario scripts.
- `data/site_index/` — Klinka 2004 site-index tables for the SBSdw1/ICHmk3
  units that apply to Gavin Lake.
- `data/benchmarks/` — the Gavin Lake Demonstration Area AAC and 2001–2005
  harvest comparison from MWP #3 Tables 34 and 36.
- `reference/` — the public AFRF reports used as benchmark sources.
- `ws4/` — the ws4 translation surface: the compiled dataset recipe, patch
  accounts, translated legacy targets, a smoke schedule, and structural parity
  evidence.
- `docs/` — the RTFM surface: instance contract, legacy intake, ws4 workflow,
  publication boundary, and the legacy-to-ws4 crosswalk.
- `notes/` — ADRs for the two-block architecture, the publication boundary,
  and the ws4 runtime decision.
- `runbooks/` — the reproducible legacy-intake and ws4 run procedures.

The legacy package is **reference and benchmark evidence**. The ws4 dataset is
the runtime lane.

## Quick start

Install ws4 with its geospatial extras and the Python tools used by the
instance:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -e /path/to/ws4[geo,opt]
```

Then rebuild the benchmark dataset and run the structural smoke simulation:

```bash
ws4 ingest \
  --matrix data/legacy_gavinlake/tracks/H \
  --fragments data/legacy_gavinlake/fragments.csv \
  --out ws4/runtime/legacy_matrix
ws4 validate --dataset ws4/runtime/legacy_matrix
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/smoke_age80_pulse.csv \
  --years 300 \
  --out ws4/runtime/smoke_age80 \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
```

The smoke schedule harvests every fragment aged 80 or more at offset 0. It is
a structural check, not a policy baseline. See `ws4/README.md` for the full
translation table and `runbooks/WS4_RUNBOOK.md` for the operator procedure.

## Current structural evidence

| Item | Value |
| --- | --- |
| Legacy blocks | 2,907 |
| Legacy net area | 5,663.66 ha |
| Tracks | 97 |
| Curve points | 48,288 |
| Initial growing stock (ws4) | 1,418,962 m³ |
| Legacy implied initial growing stock | 1,418,963 m³ |
| Relative difference | -7.2 × 10⁻⁷ |
| ws4 validation | valid |

The parity check is described in `ws4/evidence/legacy_ingest.json` and
`docs/guides/legacy-intake.rst`.

## Phase 1 baseline

The sustained-yield baseline is `ws4/schedules/baseline_evenflow.csv`. It
clearcuts at age 80, re-enters every 80 years, and balances first entries across
ten-year periods. It produces a mean of 188,677.89 m³ per period, a minimum of
177,070.07, and a maximum of 197,806.62 m³. Growing stock falls from
1,418,962.31 m³ to 495,510.56 m³ over 300 years.

The 500,000 m³ scenario harvest target and the 1,277,067 m³ growing-stock
target are not met by the baseline. The baseline is flat in absolute volume but
not within the −1 to 1 percent even-flow band.

The 500,000 is a literal scenario parameter; the archive does not record its
intent. An unattainable minimum with a linear penalty can be a deliberate
pull-up technique, especially when paired with even-flow, so the baseline
shortfall is not a verdict on the target. See
`notes/reference/legacy-target-provenance.md`. The interpretation is in
`notes/reference/gavin-baseline-findings.md`; the evidence is in
`ws4/evidence/baseline/`.

### LTSY first-guess target

The runnable first guess is `ws4/targets_gavin_ltsy.yaml`, derived from the
area-weighted mean yield curve:

- THLB proxy (`CONTCLAS = C`): 4,662.96 ha;
- CMAI: 3.599653 m³/ha/yr at age 100;
- LTSY: 16,785.06 m³/yr, or 167,850.57 m³ per ten-year period;
- ×1.1 first guess: 184,635.63 m³, rounded to 185,000.

The baseline mean of 188,677.89 m³ is about 2.2 percent above the first guess,
and the baseline meets 185,000 m³ in 22 of 30 periods. The eight misses are
177,070–184,810 m³. The 1,277,067 m³ growing-stock target is the binding
constraint. Evidence: `ws4/evidence/ltsy/`.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Plan of record and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `data/legacy_gavinlake/` | Legacy H matrix, spatial inputs, topology, scripts |
| `data/site_index/` | Klinka 2004 site-index tables |
| `data/benchmarks/` | MWP #3 Gavin Lake AAC benchmark |
| `reference/` | Public AFRF reference PDFs and citations |
| `ws4/` | ws4 translation inputs, schedules, and evidence |
| `docs/` | Guides and reference pages |
| `notes/` | ADRs, reference notes, and phase reports |
| `runbooks/` | Reproducible intake and run procedures |
| `metadata/` | Archive hash, inventory, and provenance ledgers |
| `scripts/` | Workflow validator and green dashboard |
| `tests/` | pytest suite, including the workflow self-check |

## Data publication boundary

This is a public model instance. The published surface carries the legacy model
matrix, spatial inventory, topology, scenario scripts, documentation, and
derived evidence. It does **not** carry raw cost/revenue workbooks, contractor
rates, private financial overlays, credentials, or machine-specific paths.
The legacy text files were normalized to LF and sanitized for home-directory
comments; the data values are unchanged. See
`docs/reference/data-publication-boundary.rst` and
`data/legacy_gavinlake/PROVENANCE.md`.

## Related repositories

- `UBC-FRESH/femic` — the FEMIC package and the parent checkout that links this
  instance under `external/`.
- `UBC-FRESH/femic-afrf-knifecreek-instance` — the sibling Knife Creek block
  instance.
- `UBC-FRESH/ws4` — the ws4 runtime.
- `UBC-FRESH/ubc-fresh-dev-workflow` — the planning and workflow seed.

The future merged AFRF model is reserved as `UBC-FRESH/femic-afrf-instance`.
It is not created yet. The merge contract is recorded in
`notes/adr/0003-merged-afrf-model.md`.

## License

MIT for the repository's original code and documentation. The legacy model data
and AFRF spatial inventory retain their source terms; see
`data/legacy_gavinlake/PROVENANCE.md`.

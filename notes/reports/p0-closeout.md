# Phase 0 close-out report

Phase identifier: P0
Status: approved and merged in pull request #12
Branch: `feature/p0-bootstrap`
Parent issue: see `ROADMAP.md`

## Goal

Adapt the workflow surfaces to the Gavin Lake instance, ingest the legacy H
matrix, compile a validated ws4 dataset, and record the initial structural
parity.

## What was done

- Created the repository from the UBC-FRESH dev workflow seed.
- Wrote the instance README, agent contract, roadmap, and changelog.
- Received and inventoried the legacy `AFRF.zip` archive (SHA-256
  `3652c493…03a19`).
- Sanitized the text copy to LF and removed home-directory comments.
- Derived the ws4 fragment table from `blocks.csv` and `fragments.shp`.
- Ingested the H matrix into the ws4 schema and validated the dataset.
- Recorded the structural parity: ws4 initial growing stock 1,418,962.31 m³
  versus the legacy implied 1,418,963.33 m³ (relative difference
  -7.2 × 10⁻⁷).
- Ran a structural smoke simulation with the legacy topology and patch
  accounts.
- Recorded the archive hash, file inventory, and publication boundary.
- Ran the green dashboard on the Phase 0 branch.

## Evidence

- `metadata/legacy_archive.sha256`
- `metadata/legacy_archive_inventory.csv`
- `data/legacy_gavinlake/PROVENANCE.md`
- `ws4/evidence/legacy_ingest.json`
- `ws4/evidence/smoke_age80/summary.json`
- `python scripts/dashboard.py` result: recorded in the phase pull request.

## What is not done

- The eight carbon scenarios are not translated.
- There is no reviewed baseline schedule.
- There is no optimization run.
- There is no canonical FEMIC from-scratch rebuild.
- There is no merged AFRF model.

## Risks

- The archive has no ForestModelXML, so the ws4 path is an ingest, not a recipe
  rebuild.
- The archive has no populated scenario outputs, so there is no historical
  solver replay.
- The 87 non-forest sentinel ages are clipped to zero; the raw values are kept,
  but the convention should be reviewed if a future validator treats zero-age
  non-forest differently.
- The smoke schedule is not a policy baseline.

## Recommendation

Approve Phase 0 and authorize Phase 1 (scenario translation and baseline
benchmark). Do not describe the smoke run as a harvest scenario result.

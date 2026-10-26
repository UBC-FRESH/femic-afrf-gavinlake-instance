# Gavin Lake legacy intake plan

Date: 2026-10-26
Status: Phase 0, complete pending merge

## Goal

Preserve the legacy Gavin Lake Patchworks matrix as a benchmark reference,
translate it into a validated ws4 dataset, and record the structural parity
evidence.

## Findings

- The archive is a compiled matrix, not a source recipe. There is no
  ForestModelXML.
- The H variant is complete; the N variant is not runnable.
- The H matrix has 2,907 blocks, 97 tracks, 48,288 curve points, and 5,663.66 ha.
- The block-to-fragment join is one-to-one on `RES_KEY = BLOCK`.
- 87 fragments carry `AGE_2019 = -2`, the non-forest sentinel. They are clipped
  to `F_AGE = 0` for ws4, with the raw value retained.
- The initial growing stock in ws4 is 1,418,962.31 m³. The legacy scenario's
  90% constraint implies 1,418,963.33 m³, a relative difference of -7.2 × 10⁻⁷.
- The archive's scenario output directories are empty. There is no historical
  result table to compare against.

## Translation decisions

- Ingest the H matrix with `ws4 ingest`; do not reconstruct an XML recipe.
- Commit the sanitized package and the derived fragment table.
- Keep the legacy block, track, curve, treatment, and account names.
- Translate the timber-harvest scenario into
  `ws4/targets_legacy_harvest.yaml`.
- Keep the patch accounts as reporting surfaces; do not invent patch targets.
- Defer the eight carbon scenarios to Phase 1 and Phase 4.

## Open questions

1. Does the H matrix's `CONTCLAS` split need a separate non-forest track, or is
   the zero-yield track enough?
2. Should the primary benchmark use all fragments or the productive-forest
   subset?
3. What is the first reviewed baseline schedule?
4. Can a legacy scenario output be recovered from another source?
5. Does the canonical FEMIC rebuild have a source-data path, or is the
   compiled matrix the permanent input?

## Next steps

1. Translate the remaining scenario catalog.
2. Build a reproducible baseline schedule.
3. Compare account trajectories and record accepted variances.
4. Decide whether to attempt a canonical FEMIC rebuild.
5. Record the merge contract with Knife Creek.

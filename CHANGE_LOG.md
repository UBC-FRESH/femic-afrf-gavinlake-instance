# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap
status and the GitHub issue comments.

## 2026-10-26

- Created `femic-afrf-gavinlake-instance` from the UBC-FRESH dev workflow seed.
  The seed supplied the agent contract, roadmap, docs skeleton, validator,
  dashboard, and tests.
- Received the legacy AFRF Patchworks archive (`AFRF.zip`, SHA-256
  `3652c493…03a19`). The archive contains the Gavin Lake H matrix, spatial
  inventory, topology, pin, and scenario scripts. It does not contain a
  ForestModelXML recipe or populated scenario outputs.
- Ingested the H matrix into the ws4 schema with a prepared fragment table.
  The dataset validates and contains 2,907 fragments, 97 tracks, and 48,288
  curve points over 5,663.66 ha.
- Recorded the structural parity check: ws4 initial growing stock is
  1,418,962.31 m³; the legacy scenario's 90% constraint implies 1,418,963.33
  m³ (relative difference -7.2 × 10⁻⁷).
- Added the sanitized legacy package under `data/legacy_gavinlake/`, the ws4
  translation surfaces under `ws4/`, and the provenance ledgers under
  `metadata/`.
- Ran the green dashboard in the Phase 0 branch. The plan is to merge this
  bootstrap via the Phase 0 pull request and then register the repository as a
  submodule of `UBC-FRESH/femic` at `external/femic-afrf-gavinlake-instance`.
- Linked Phase 0 to parent issue #1 and child issues #2-#6. Phase 1 (scenario translation and baseline benchmark) is planned under parent issue #7 and is not active.
- Merged Phase 0 in pull request #12 (commit `3a00cd3`). P0 is complete; P1 remains planned under parent issue #7.

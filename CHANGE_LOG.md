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
- Activated Phase 1 under parent issue #7 and recorded all nine legacy
  scenarios in `ws4/scenarios/legacy_catalog.yaml`. The timber-harvest scenario
  is translated; the eight carbon scenarios are deferred because the compiled
  matrix lacks the runtime duplicate stock/flux accounts and the target units
  are unresolved.
- Added `ws4/build_baseline_schedule.py` and generated
  `ws4/schedules/baseline_evenflow.csv` (10,113 rows, 2,907 blocks). The
  baseline clearcuts at age 80 and re-enters every 80 years.
- Simulated the baseline for 300 years. Mean harvest is 188,677.89 m³ per
  ten-year period, minimum 177,070.07, maximum 197,806.62. Growing stock falls
  from 1,418,962.31 m³ to 495,510.56 m³.
- Recorded the benchmark variance: the 500,000 m³ harvest target and the
  1,277,067 m³ growing-stock target are not met by the baseline on the compiled
  H matrix (target intent not recorded; see the later correction). The target
  report has 31 below, 26 above, and 4 met rows.
- Added the baseline evidence under `ws4/evidence/baseline/`, the findings note
  `notes/reference/gavin-baseline-findings.md`, and the Phase 1 closeout report.
- Merged Phase 1 in pull request #13 (commit `cc414a6`). P1 is complete; P2 remains planned.
- First correction of the 500,000 m³ provenance (superseded by the next
  entry). It recorded the MKRF ancestry of the literal but overreached by
  treating that as proof the value was not an AFRF target. Added
  `notes/reference/legacy-target-provenance.md`.
- Corrected the target-provenance note again to avoid inferring modeler
  intent. The 500,000 is a literal scenario parameter; the archive does not
  record whether it is a deliberate pull-up target, a feasible floor, a template
  value, or an exploratory setting. An unattainable minimum with a linear
  penalty, paired with even-flow, is a legitimate pull-up technique. The
  baseline shortfall is now reported as a trajectory result, not as a verdict
  on the target or on AFRF policy. See
  `notes/reference/legacy-target-provenance.md`.
- Added `ws4/estimate_ltsy_target.py` and derived the first-guess LTSY
  harvest target. On the productive THLB proxy (`CONTCLAS = C`, 4,662.96 ha),
  the area-weighted mean yield CMAI is 3.599653 m³/ha/yr at age 100. LTSY is
  16,785.06 m³/yr, or 167,850.57 m³ per ten-year period. The ×1.1 first guess is
  184,635.63 m³, rounded to 185,000.
- Added `ws4/targets_gavin_ltsy.yaml` as the runnable first-guess target. The
  baseline meets 185,000 m³ in 22 of 30 periods; the eight misses are
  177,070–184,810 m³. The 1,277,067 m³ growing-stock target is the binding
  constraint. The literal 500,000 remains in
  `ws4/targets_legacy_harvest.yaml` as a parity reference.
- Added the LTSY evidence under `ws4/evidence/ltsy/` and the P1.5 task (#14).

## 2026-10-27

- Activated P1.6 (#22) to add public reference benchmarks without changing the
  legacy H matrix or the runnable LTSY target.
- Added the Klinka et al. 2004 site-index tables (8.2.1–8.2.4) as
  `data/site_index/klinka_2004_site_index.csv`. The Gavin Lake block is in the
  SBSdw1 and ICHmk3 units; the IDFxm/IDFdk3 rows are included for the sibling
  Knife Creek instance. The values are potential site index, not a measured
  Gavin growth curve.
- Added the Gavin Lake Demonstration Area AAC and 2001–2005 harvest comparison
  from AFRF Management and Working Plan #3 Tables 34 and 36 as
  `data/benchmarks/mwp3_gavin_aac.csv`: 2.4 ha/year clearcut, 3.0 ha/year
  partial cut, 2.4 ha/year salvage, 7.8 ha/year total on a 478 ha net harvest
  land base with a 100-year cycle; actual 2001–2005 was 31.8 ha/year total.
- Recorded that the GL working circle is not the legacy Gavin model's
  4,662.96 ha THLB proxy or its 80-year clearcut rotation. The AAC is a public
  management-plan benchmark, not the legacy scenario intent.
- Added the public AFRF report PDFs and `reference/README.md` so the benchmark
  provenance is self-contained. They are UBC AFRF publications, not OGL.
- Confirmed that MWP #3 Figure 11 is Knife Creek-specific and that Klinka's
  quantitative content is in its tables, not its photo figures. No figrecover
  pass was needed for Gavin.

## 2026-10-31

- Activated P7, roads, log sorts, and mills, under parent issue #24 on
  `feature/p7-roads-logs-mills`. The phase plan is
  `planning/p7-roads-logs-mills.md`.

- Built the Gavin Lake screening delivered-wood layer. Fetched the public
  2025 VRI and public tenure-road layer around the block; built a connected
  route graph (193 road segments, 178 components joined by 177 synthetic
  connectors, 5 candidate sawlog mills); ran the 300-year baseline through
  `ws4.roads`; and split routed volume by VRI species and the BC interior
  June-August 2026 sort mix. Result: 5,660,337 m3 from 2,907 fragments,
  57.18 M CAD haul, 0.59 M CAD maintenance, and about 683.9 M CAD gross value.
  All volume goes to `destination.MILL_107_LBR` because no mill demand or
  capacity constraint is available. See `data/delivered_wood/gavin/README.md`.

- The public road layer is only 19.3 km against 112.2 km in MWP #3 Table 37.
  The route rates are TSA23 proxies, mill haul is a straight-line abstraction,
  and the sort mix and prices are regional BC references. This is a screening
  layer, not an operational or legal model.

## 2026-10-31

- Added the Gavin 2025 VRI starting layer
  (`runbooks/build_gavin_vri_start.py`,
  `data/inventory/gavin_vri_2025_start.{csv,gpkg}`). The area-weighted VRI age
  is 125.3 years vs 99.4 years for the legacy ages advanced to 2025; 1,606 of
  2,907 fragments differ by more than 20 years. This is the rebuild input; the
  compiled legacy matrix still uses `AGE_2019`.

- Added the partial Gavin 2013 canopy tree inventory
  (`runbooks/detect_gavin_2013_trees.py`,
  `data/lidar/gavin_2013/`). The 11 2013 LAS tiles cover 339 ha of the 5,664 ha
  block and produce 166,188 canopy trees. Added the 111-fragment piece-size
  table and a validated FHOPS tree-inventory pilot for fragment 323. The full
  tree files are large and remain uncommitted.

- The OneDrive payload has no 2019 or 2024 Gavin LiDAR; the 2009 FUSION
  LIDARBIN is not readable by the current pipeline. Gavin tree-level coverage
  is therefore partial.

- Diagnosed the 2009 LiDAR as valid FUSION `LIDARBIN`, not corrupted LAS. The
  files start with `LIDARBIN`; DataLad `fsck` passes. The failure was our
  `laspy` reader assuming `LASF`. Installed FUSION/LDV 4.61 and processed the
  full 2009 Gavin coverage with `Catalog`, `GridSurfaceCreate`, `CanopyModel`,
  and `CanopyMaxima`. Result: 100 `pt` tiles, 1,116,962 canopy trees, 197 TPH,
  mean height 15.0 m, mean DBH estimate 19.8 cm. See
  `notes/reference/ubc-2009-lidar-format-fix.md` and
  `data/lidar/gavin_2009/README.md`. No reupload is needed.

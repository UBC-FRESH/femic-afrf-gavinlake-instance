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
  LIDARBIN is valid and was processed with FUSION. Gavin tree-level coverage is
  full for 2009, with the 2013 inventory retained as a partial check.

- Diagnosed the 2009 LiDAR as valid FUSION `LIDARBIN`, not corrupted LAS. The
  files start with `LIDARBIN`; DataLad `fsck` passes. The failure was our
  `laspy` reader assuming `LASF`. Installed FUSION/LDV 4.61 and processed the
  full 2009 Gavin coverage with `Catalog`, `GridSurfaceCreate`, `CanopyModel`,
  and `CanopyMaxima`. Result: 100 `pt` tiles, 1,116,962 canopy trees, 197 TPH,
  mean height 15.0 m, mean DBH estimate 19.8 cm. See
  `notes/reference/ubc-2009-lidar-format-fix.md` and
  `data/lidar/gavin_2009/README.md`. No reupload is needed.

- Built a real Tree Lab case for Gavin Lake GL_4123
  (`data/tree_lab/gl_4123/`) from the 2009 inventory: 400 trees, 6.967 ha,
  200.3 m3/ha, 3.49 m3/stem. Ran FHOPS `tree system` with one feller-buncher,
  two grapple skidders, one processor, and one loader: 1,384.4 m3 processed,
  52.4 h makespan, 46 truck loads, no warnings. Exported a 400-tree/800-log
  `tree scene` and assembled a local playback bundle at
  `runs/gl_4123/view/`. The case manifest follows
  `fhops.tree_lab.case.v1`; it still needs to be copied into the Tree Lab
  `sandbox/cases/` host or validated by the Tree Lab runner. Added the
  tree-scale chain: `tree stems` produced 3,061 logs (3,007 sawlog, 54 pulp)
  with -0.79% volume difference; `tree simulate` processed all 400 trees in
  4.78 h; `tree replay` completed with zero discrepancies. The single processor
  is the system bottleneck at 80.8% utilisation; a second processor cuts the
  makespan from 52.4 to 30.8 h, and a third truck cuts it to 27.0 h.

- Built the six-AU Gavin Lake FVS-BC creative-silviculture pilot
  (`runbooks/build_gl_fvsbc_pilot.py`, `data/fvsbc/gl_pilot/`). The AUs span
  ICHmk3/SBSdw1, ages 60-162, and FD/SE/CW/BL/AT. The 2009 LiDAR list supplies
  piece size; total BA is scaled to the Williams Lake PSP BEC/age analog
  (32.9-52.1 m2/ha). Ran 36 cases: untreated plus commercial thinning, fuel
  mitigation, irregular selection, shelterwood, and variable retention. Added
  `runbooks/build_gl_fvsbc_transitions.py` for the 5 cm DBH distributions and
  ten-year live/harvest/mortality transitions. FVS-BC reads the BC variant's
  basal-area targets in m2/ha, and a cycle-number target schedules at the first
  year of that cycle. The pilot is not calibrated, has no regeneration model,
  and is not a full-estate state library.

- Expanded the FVS-BC creative-silviculture library to all 79 productive
  Gavin Lake AUs (`data/fvsbc/gl_all/`). The run has 474 cases (79 x 6
  treatments), 5,214 curve rows, and 2.51 million per-tree trajectory rows.
  The LiDAR piece-size list is scaled to a Williams Lake PSP BEC/age BA analog
  for every AU (mean target 45.5 m2/ha, mean initial 45.6 m2/ha). Added
  `runbooks/build_gl_fvsbc_legacy_comparison.py`. The median difference from
  the legacy yield curve is +18.1% at current age and +69.1% at current age
  +100; the latter compares an untreated 100-year FVS projection with an
  80-year clearcut rotation, so it is a screening comparison, not parity. The
  next step is ingesting these curves and transitions into the ws4 matrix
  contract; this folder is the source evidence, not the matrix.

- Compiled the full FVS-BC library into a ws4-compatible single-entry state graph
  at `data/fvsbc/gl_all/ws4_state_graph/` with
  `runbooks/build_gl_ws4_state_graph.py`: 79 AU fragments, 474 tracks, 395
  treatment edges, 9,638 curves, and `ws4 validate` accepted. A 100-year
  baseline run ends at 3,100,745 m3; a CT60 treatment on every AU ends at
  2,151,172 m3 over the same 4,663.0 ha. The graph is a v0: AU-scale fragments,
  one entry offset per AU, and the post-treatment FVS cycle shifted to the entry
  age. Repeated entries and harvested products still need age-specific tracks
  and a cut-volume compile.

- Added harvest total, sawlog, and pulp product curves to the ws4 state graph
  from `cut_list.parquet`, using `MCuM x TPH` per hectare and a 20 cm sawlog
  threshold. The validated graph now has 11,939 curves, 1,659 product rows, and
  395 treatment edges. A CT60 treatment on all 79 AUs yields 466,183 m3 of
  harvest (443,393 sawlog, 22,789 pulp) in the 100-year ws4 run.

- Added a second-entry FVS-BC chain (`runbooks/build_gl_fvsbc_multientry.py`,
  `data/fvsbc/gl_multientry/`). For 79 AUs and two first-entry treatments, the
  year-10 post-treatment tree list is filtered by the first cut list and re-run
  for a second 100-year entry: 158 runs, 1,738 summary rows, median initial
  difference -0.9%, median second-entry growth +71.5 m3/ha.
- Extended the ws4 state graph to two entries
  (`data/fvsbc/gl_all/ws4_state_graph/`): 632 tracks, 553 edges, 15,415 curves,
  and a valid two-entry schedule. The 100-year final feature volume is 3,100,745
  m3 baseline, 2,151,172 m3 with CT60 once, and 1,352,213 m3 with CT60 twice.
  Second-entry harvest products were compiled in the following entry.

- Compiled the second-entry cut list into the two-entry ws4 graph. The graph now
  has 15,889 curves and 2,133 product rows. The 100-year CT60-twice run ends at
  1,352,213 m3 and produces 466,183 m3 in the first entry plus 463,830 m3 in the
  second entry (930,013 m3 total).

- Built the age-binned spatial ws4 graph
  (`runbooks/build_gl_ws4_spatial_graph.py`,
  `data/fvsbc/gl_all/ws4_spatial_graph/`). It carries 1,505 productive
  fragments (1,402 AU-9999 fragments excluded), 3,016 tracks, 2,639 treatment
  edges, 75,677 curves, and 7,917 products. Each fragment is assigned to an AU
  and 10-year age-bin untreated track; treatment edges use the bin age. A
  100-year baseline ends at 3,112,737 m3; CT60 twice ends at 1,352,213 m3 and
  harvests 930,013 m3. The graph is validated.

- Built the entry-age cohort graph
  (`runbooks/build_gl_ws4_cohort_graph.py`,
  `data/fvsbc/gl_all/ws4_cohort_graph/`): 1,505 productive fragments, 19,227
  tracks, 18,850 treatment edges, 493,624 curves, 56,550 products, and ten entry
  offsets (0-90 years) for five treatments. Added
  `runbooks/build_gl_evenflow_schedule.py`; the greedy one-CT60-per-block
  schedule produces 46,618 m3 in each ten-year period, essentially flat, and a
  final standing volume of 1,815,758 m3. This is a thinning flow, not a
  final-harvest AAC; the legacy LTSY target is 185,000 m3 per period.

- Added clearcut final-harvest cohorts to the entry-age cohort graph. The graph
  now has 22,997 tracks, 22,620 treatment edges, 1,266,474 curves, and 67,860
  products. Three schedules were built:
  - thinning only: 46,618 m3 per decade, flat;
  - all-block final harvest: 214,789 m3 per decade, final inventory zero;
  - LTSY-target final harvest: 184,796 m3 per decade on 618 blocks, final
    standing inventory 438,394 m3.
  The LTSY schedule is within 0.1% of 185,000 m3 and flat to 11 m3 per decade,
  but it is a 100-year liquidation, not a perpetual AAC. Clearcut yield is the
  standing volume at entry; no regeneration is modelled.

- Added the planted bare-ground regeneration library
  (`runbooks/build_gl_fvsbc_regeneration.py`, `data/fvsbc/gl_regen/`): 79 AUs,
  869 rows, mean 100-year volume 480.4 m3/ha, BA 46.7 m2/ha, top height 34.4 m.
  The cohort graph now routes clearcut entries into those planted curves. The
  LTSY-target schedule remains 184,796 m3 per decade, while final standing
  volume rises from zero to 1,156,523 m3 because harvested blocks regrow. This
  is planted second-rotation growth, not natural regeneration or a second
  harvest.

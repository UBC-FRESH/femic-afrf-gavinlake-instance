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

## 2026-11-22

- Downloaded and clipped the approved UWR boundary and stand-structure habitat
  classes from the BC Geographic Warehouse; derived layers are in
  `data/derived/gavin_mdwr/`.
- Gavin UWR clip: U-5-002 / dwl_9 Beaver Valley North, 2,726.42 ha.
- Stand-structure classes: High 697.92 ha, Moderate 1,013.18 ha, Low 1,015.33 ha.
- Confirmed GWM 10 defines frost-prone as medium, high or very high summer
  frost hazard; FRDA Report 157 Table 3 and the 5 m DEM make a screening
  classification possible.
- Corrected earlier notes that treated UWR and stand-structure data as
  unavailable. Adjusted Appendix 9 compartment boundaries remain the only
  unresolved spatial layer.
- The group estate remains 2,797.5 ha versus the 2,726.42 ha UWR clip; the
  ~71 ha difference is unresolved. No model result changed.
- Clarified GWM 10 opening sizes: transition other 0.1–0.7 ha / frost
  0.1–0.3 ha; deep other 0.1–1.0 ha / frost 0.1–0.4 ha.
- Added a preliminary frost screen from FRDA Report 157 Table 3, the 5 m DEM
  and a 500 m TPI. It is a screening diagnostic, not a legal determination.
- 540 assigned openings (186.4 ha) are frost-prone; 291 assigned openings
  (142.2 ha) exceed the frost cap. 181 assigned openings have 42.6 ha outside
  the approved UWR.
- 499 assigned openings (221.6 ha) fail an opening-size or UWR test. The group
  layout must be rebuilt; no public model result changed.
- Added a clipped-and-capped layout repair: 27,110 groups / 2,722.37 ha, 4,671
  assigned openings / 1,386.43 ha, zero cap violations, zero outside-UWR
  groups. Assigned area falls by 46.36 ha (42.58 ha outside UWR plus 3.78 ha
  dropped small pieces).
- The repair is not a cohort result; the public group result remains the old
  layout's 0.679M m³ / 26-of-30 diagnostic.
- Ran the legal s40 cohort state on the repair: 27,083 groups, 1,427 blocks,
  12,534 cuts, 1,684.1 ha cut, 629,809 m³ harvested, final stock 1,111,922 m³,
  final BA 180,249 m².
- The cohort is 4.3% below the old legal s40 cohort (658,199 m³), mainly an
  area effect. It cuts all groups, not only the 4,671 assigned openings
  (1,386.4 ha); no regrown phase result yet.
- Ran the assigned-openings-only cohort: 3,743 groups cut at least once
  (1,106.79 ha unique), 928 assigned groups (279.64 ha) remain uncut because
  the cohort script ignores layout entry offsets. Harvested 499,597 m³; final
  state 554,774 m³; final BA 96,950 m². The final state covers only the
  assigned area, not the full estate.
- Built the assigned entry-offset ledger: all 4,671 openings cut once,
  1,386.43 ha, 504,601 m³, no uncut openings. Mean cut BA 82.2 m²/ha; 612
  openings (174.9 ha) are below 40 m²/ha at entry, but GWM 6 is applied at the
  stand/block level. First-decade volume 148,505 m³; no phase result.
- Ran the regrown phase optimizer on the entry ledger: 579,763 m³, mean
  19,325 m³, max 30,950 m³, 26/30 periods in band. Late periods 260–290 are
  6,603 / 3,944 / 3,841 / 3,474 m³; no ceiling violations.
- The 119-year phase cap and early assigned-entry concentration leave too small
  a late-entry pool to fill the tail. No further phase restart recommended.

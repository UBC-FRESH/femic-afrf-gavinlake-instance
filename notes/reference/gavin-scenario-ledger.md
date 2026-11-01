# Gavin Lake scenario ledger

Date: 2026-11-01
Status: authoritative scenario record for the Gavin Lake FVS/ws4/AAC work
Repository: `femic-afrf-gavinlake-instance`

Use this ledger before rerunning an experiment. It records what was run, the
inputs, the result, and whether the result is accepted, rejected, or only a
screening step. If this file and an older README disagree, this file is the
current record and the older README is stale.

## 1. Provenance and inputs

### 1.1 Tree inventory

- Source: 2009 UBC/AFRF FUSION `LIDARBIN`, processed with FUSION/LDV 4.61.
- The 2009 `.las` files are valid `LIDARBIN`, not corrupted LAS.
- Full Gavin coverage: 100 `pt` tiles, 1,116,962 canopy trees, 197 TPH.
- Mean height 15.0 m; mean DBH estimate 19.8 cm.
- This is a canopy inventory, not a CFI. Species are VRI shares; DBH is height
  allometry.

### 1.2 VRI and PSP

- Starting layer: `data/inventory/gavin_vri_2025_start.gpkg`.
- 2,907 fragments total; 1,505 productive fragments (4,663.0 ha).
- The remaining 1,402 fragments are AU 9999, the non-productive/unclassified
  group, and are excluded from the FVS estate runs.
- PSP density correction: Williams Lake TSA plots, same BEC and age window.
- The LiDAR list supplies piece size; the PSP analog supplies total BA.
- Mean target BA 45.5 m2/ha; mean initial BA 45.6 m2/ha across 79 AUs.

### 1.3 Legacy model

- Legacy H matrix: `ws4/runtime/legacy_matrix/`.
- Legacy rotation: 80-year clearcut.
- Legacy LTSY first guess: 185,000 m3 per ten-year period.
- Legacy yield comparison is a screening comparison, not a parity test.

## 2. FVS-BC scenario families

### S1. Six-AU FVS-BC pilot

Purpose: test the FVS-BC treatment library and the PSP density correction on a
representative subset.

- File: `data/fvsbc/gl_pilot/`
- AUs: 2, 302, 352, 312, 802, 502.
- Treatments: `untreated`, `ct60`, `fuel50`, `selection80`, `shelterwood40`,
  `vr20`.
- Runs: 36.
- Curves: 396.
- Tree rows: 211,505.
- Cut rows: 12,022.

Final merchantable volume at year 100, m3/ha:

| AU | untreated | ct60 | fuel50 | selection80 | shelterwood40 | vr20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 758 | 505 | 423 | 531 | 20 | 276 |
| 302 | 518 | 298 | 223 | 352 | 19 | 296 |
| 352 | 659 | 489 | 395 | 414 | 22 | 378 |
| 312 | 538 | 541 | 495 | 404 | 31 | 457 |
| 802 | 739 | 500 | 392 | 561 | 19 | 380 |
| 502 | 507 | 310 | 253 | 420 | 40 | 230 |

Decision: accepted as the pilot. It established that the machinery works and
that the LiDAR canopy density alone is not a total stand density.

### S2. Full 79-AU FVS-BC library

- File: `data/fvsbc/gl_all/`
- AUs: 79 productive AUs.
- Runs: 474 = 79 x 6 treatments.
- Curves: 5,214.
- Tree rows: 2,510,760.
- Cut rows: 161,337.
- Warnings: 474, all `FVS03` forest-code warnings; none fatal.

Treatments:

| ID | Definition |
| --- | --- |
| `untreated` | no harvest |
| `ct60` | commercial thinning from below, residual 60% BA at year 0 |
| `fuel50` | fuel-mitigation thinning from below, residual 50% BA at year 0 |
| `selection80` | irregular selection, residual 80% BA in cycles 1, 3, 5, 7, 9 |
| `shelterwood40` | seed cut to 40% BA at year 0; final removal in cycle 4 |
| `vr20` | variable retention from above, residual 20% BA at year 0 |

Legacy comparison:

- median current-age difference: **+18.1%**;
- median current-age +100 difference: **+69.1%**;
- 69/79 AUs have a legacy curve covering current age; 79/79 cover age +100.

The +69.1% is expected: untreated FVS for 100 years versus an 80-year clearcut
curve. It is not a parity failure.

Decision: accepted as the source growth library.

### S3. 200-year untreated curves

- File: `data/fvsbc/gl_untreated_200y/`
- Runs: 79.
- Curves: 1,659.
- Tree rows: 842,069.
- Purpose: provide clearcut volume at entry offsets beyond 100 years.

Decision: accepted as the late-entry supplement.

### S4. Second-entry FVS chain

- File: `data/fvsbc/gl_multientry/`
- Runs: 158 = 79 AUs x `ct60`, `selection80`.
- Curves: 1,738.
- Method: year-10 post-treatment tree list, remove first-entry cut trees,
  regroup by `TreeId`, run another 100-year case.
- Median first-post versus second-initial difference: **+3.8%**.
- Median second-entry growth: **+72.5 m3/ha**.
- Second-entry cut rows: 5,576; cut file 389 KB.

Decision: accepted as second-entry evidence. This is two chained FVS cases, not
one continuous projection.

## 3. ws4 model scenarios

### S5. AU-scale state graph v1

- File: `data/fvsbc/gl_all/ws4_state_graph/`
- Fragments: 79 AU-scale fragments, 4,663.0 ha.
- Tracks: 632.
- Treatment edges: 553.
- Curves: 15,889.
- Products: 2,133.
- Validation: passed.

100-year runs:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline | 3,100,745 m3 |
| CT60 once | 2,151,172 m3 |
| CT60 twice | 1,352,213 m3 |

CT60 harvest:

- first entry: 466,183 m3 (443,393 sawlog + 22,789 pulp);
- second entry: 463,830 m3 (460,558 sawlog + 3,272 pulp);
- total: 930,013 m3.

Decision: accepted as an AU-scale demonstration. It is not spatial.

### S6. Age-binned spatial graph v1

- File: `data/fvsbc/gl_all/ws4_spatial_graph/`
- Fragments: 1,505 productive fragments, 4,663.0 ha.
- Tracks: 3,016.
- Treatment edges: 2,639.
- Curves: 75,677.
- Products: 7,917.
- Validation: passed.
- Each fragment is assigned to an AU and 10-year age-bin track.
- Baseline: 3,112,737 m3 at 2099.
- CT60 twice: 1,352,213 m3; harvest 930,013 m3.

Decision: accepted as the first spatial graph. It is superseded for scheduling
by the cohort graph.

### S7. Entry-age cohort graph v4

- File: `data/fvsbc/gl_all/ws4_cohort_graph/`
- Fragments: 1,505 productive fragments, 4,663.0 ha.
- Tracks: 26,390.
- Treatment edges: 26,013.
- Curves: 672,699.
- Products: 78,039.
- Entry offsets: 0, 10, ..., 180 years.
- Treatments: `ct60`, `fuel50`, `selection80`, `shelterwood40`, `vr20`, plus
  `clearcut`.
- Validation: passed.

One-rotation schedules:

| Schedule | Harvest per decade | Notes |
| --- | ---: | --- |
| thinning only | 46,618 m3 | one CT60 per block, flat |
| all-block final harvest | 214,789 m3 | every block clearcut once |
| LTSY-target final harvest | 184,796 m3 | 618 blocks; flat to 11 m3 |

The LTSY-target schedule leaves 887 blocks standing. Final standing volume after
planted regeneration: **1,156,523 m3**.

Decision: accepted as the current scheduling graph. The 184,796 m3 schedule is a
100-year liquidation, not a perpetual AAC.

## 4. AAC and second-rotation scenarios

### S8. Second-rotation test

- File: `data/fvsbc/gl_second_rotation/`
- Base: 618 blocks from the 184,796 m3 first-rotation schedule.
- Second rotation: planted FVS curve at age 80.
- Second-rotation area: 4,000.0 ha.
- Second-rotation total: 1,133,877 m3.
- Mean: **113,388 m3/decade**.
- Does it hold 185,000? **No.**

By period:

| Period | Second-rotation m3 |
| ---: | ---: |
| 80 | 153,797 |
| 90 | 155,694 |
| 100 | 132,302 |
| 110 | 117,305 |
| 120 | 111,101 |
| 130 | 103,900 |
| 140 | 95,057 |
| 150 | 93,232 |
| 160 | 90,685 |
| 170 | 80,804 |

Decision: accepted as a negative result. 185,000 m3/decade is not sustained on
this land base.

### S9. 200-year greedy schedule

- File: `data/fvsbc/gl_second_rotation/schedule_200_year.csv`
- All 1,505 blocks, first and second cuts.
- Mean: **172,609 m3/decade**.
- Minimum: **0**.
- Maximum: **241,519**.
- First-rotation total: 2,132,492 m3.
- Second-rotation total: 1,319,694 m3.
- Shape: about 241,500 m3/decade through period 100, then declining to zero at
  period 190.
- Target-150,000 greedy: 308 blocks, mean **112,709 m3/decade**, late periods
  underfilled.

Decision: rejected as an even-flow schedule. It is a diagnostic only.

### S10. Joint first/second optimizer attempt

- Prototype: `runbooks/build_gl_joint_optimizer.py` was tried and removed.
- LP relaxation minimum: **186,768 m3/decade**.
- Per-block rounding minimum: **171,722 m3/decade**.
- MILP with ~28,000 binaries: timed out at 120 s.
- No schedule was committed.

Decision: rejected. A formal MILP, column generation, or another exact approach
is required. Do not repeat LP-plus-argmax rounding and call it an AAC.

## 5. Operations and delivered-wood scenarios

### S11. Tree Lab / FHOPS ground system, Gavin GL_4123

- File: `data/tree_lab/gl_4123/`
- 400 trees, 6.967 ha, 200.3 m3/ha, 3.49 m3/stem.
- `tree stems`: 3,061 logs; 3,007 sawlog + 54 pulp; -0.79% volume diff.
- `tree simulate`: 400 trees, 4.78 h, zero unreachable.
- `tree replay`: 400 trees, zero discrepancies.
- `tree system`: 1,384.4 m3, 46 loads, 52.4 h.
- Bottleneck: single processor at 80.8% utilisation.
- 2 processors: 30.8 h.
- 2 processors + 3 trucks: 27.0 h.

Sensitivity:

| Configuration | Makespan h | Feller | Skidder | Processor | Loader |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 processor, 2 trucks | 52.4 | 9.1% | 14.0% | 80.8% | 38.6% |
| 2 processors, 2 trucks | 30.8 | 15.5% | 23.9% | 69.0% | 65.8% |
| 2 processors, 3 trucks | 27.0 | 17.7% | 27.3% | 78.8% | 75.0% |

Decision: accepted as a reference execution case, not an operational plan.

### S12. Gavin delivered-wood screening

- File: `data/delivered_wood/gavin/`
- 2,907 fragments routed through 193 public-road segments and 5 candidate mills.
- 5,660,337 m3 routed.
- Haul: 57.18 M CAD.
- Maintenance: 0.59 M CAD.
- Gross value: 683.9 M CAD.
- Largest sort: Df-Larch sawlog, 2,122,049 m3, 264.0 M CAD.
- All volume goes to the least-cost mill because mill demand/capacity are not
  modelled.

Decision: screening only. Not an operational or legal-access result.

### S13. KC tree inventory and model-of-record context

- KC model of record: `ws4/dataset_kc_au_stages_split_volume_v1`, 211 split
  blocks.
- 2024 LiDAR canopy inventory: 278,318 trees; block 78 FHOPS pilot: 245 trees,
  validated.
- KC is predominantly IDF and selection/uneven-aged. Do not apply the Gavin
  clearcut AAC logic to KC without a separate KC state library.

### S14. KC delivered-wood screening

- File: `data/delivered_wood/kc/`
- 75 road segments, 13 components, 4 candidate mills.
- 540,192 m3 from 126 blocks.
- Haul: 3.14 M CAD; maintenance: 1.61 M CAD.
- Gross value: 65.3 M CAD.

Decision: screening only.

## 6. Settled findings

1. The 2009 LiDAR is valid FUSION `LIDARBIN`. The earlier “unreadable” finding
   was a reader assumption, not corrupt data.
2. LiDAR canopy density is not total stem density. Without PSP BA scaling, FVS
   stands are far too sparse.
3. FVS-BC reads `THINBBA`/`THINABA` targets in **m2/ha**, not ft2/ac.
4. The BC thinning cycle field is one-based; cycle 4 schedules at year 30.
5. The 185,000 m3 first-rotation schedule is a liquidation, not a sustained AAC.
6. A planted second rotation on the same 4,000 ha supports about 113,000
   m3/decade, not 185,000.
7. Extending to 200 years raises the mean to about 172,600 m3/decade but does not
   produce an even flow; the range is 0–241,519.
8. Greedy scheduling cannot solve the joint first/second timing problem.
9. The FVS curves are state-relative; forcing them into the legacy age-domain
   matrix would create invalid semantics.

## 7. Rejected paths and do-not-repeat list

- Do not call the 2009 LiDAR unreadable. It is valid FUSION LIDARBIN.
- Do not use LiDAR canopy TPH as total stand density.
- Do not ingest state-relative FVS curves directly into the legacy matrix.
- Do not publish 185,000 m3/decade as a sustained AAC.
- Do not use the 200-year greedy schedule as an AAC.
- Do not use LP relaxation plus argmax rounding as a schedule.
- Do not use the Tree Lab 900-tree synthetic case as a representation of the
  real Gavin inventory.
- Do not treat AU 9999 as productive forest.

## 8. Open questions and next queue

1. Formal joint first/second-rotation optimizer. Needed to establish whether any
   even flow above 113,000 m3/decade is feasible on this land base.
2. Natural regeneration versus planted regeneration; ingress and brushing
   assumptions.
3. Current GWM order and legal stand-structure map.
4. Mill demand, capacity, accepted sorts, and delivered-wood routing.
5. Update the stale per-folder READMEs to point at this ledger.
6. Merge Gavin PR #25 and KC PR #126 when approved.

## 9. Reproduce

From the repository root:

```bash
python runbooks/build_gl_fvsbc_pilot.py --all-aus --workers 6
python runbooks/build_gl_fvsbc_transitions.py \
  --pilot-dir data/fvsbc/gl_all --out-dir data/fvsbc/gl_all
python runbooks/build_gl_fvsbc_legacy_comparison.py \
  --fvs-dir data/fvsbc/gl_all
python runbooks/build_gl_fvsbc_regeneration.py
python runbooks/build_gl_ws4_state_graph.py
python runbooks/build_gl_ws4_spatial_graph.py
python runbooks/build_gl_ws4_cohort_graph.py \
  --offsets 0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180
python runbooks/build_gl_evenflow_schedule.py \
  --dataset data/fvsbc/gl_all/ws4_cohort_graph \
  --prefix CLEARCUT_E --target 176000 \
  --out data/fvsbc/gl_all/ws4_cohort_graph/schedules/evenflow_ltsy.csv
python runbooks/build_gl_second_rotation_test.py
python runbooks/build_gl_second_rotation_schedule.py \
  --dataset data/fvsbc/gl_all/ws4_cohort_graph
ws4 validate --dataset data/fvsbc/gl_all/ws4_cohort_graph
```

The PSP extract is expected at `../../inv01-data/psp`, or pass `--psp-dir`.

## 10. Artifact index

| Artifact | Purpose |
| --- | --- |
| `data/fvsbc/gl_pilot/` | six-AU FVS pilot |
| `data/fvsbc/gl_all/` | 79-AU FVS library |
| `data/fvsbc/gl_untreated_200y/` | 200-year untreated curves |
| `data/fvsbc/gl_multientry/` | second-entry chain |
| `data/fvsbc/gl_regen/` | planted regeneration curves |
| `data/fvsbc/gl_second_rotation/` | second-rotation and 200-year tests |
| `data/fvsbc/gl_all/ws4_state_graph/` | AU-scale two-entry graph |
| `data/fvsbc/gl_all/ws4_spatial_graph/` | age-binned spatial graph |
| `data/fvsbc/gl_all/ws4_cohort_graph/` | entry-age cohort graph and schedules |
| `data/tree_lab/gl_4123/` | real Tree Lab/FHOPS case |
| `data/delivered_wood/gavin/` | Gavin delivered-wood screening |
| `data/delivered_wood/kc/` | KC delivered-wood screening |

> **Current scenario record:** `notes/reference/gavin-scenario-ledger.md`.
> Some sections below describe earlier graph versions; use the ledger for the
> authoritative current numbers and decisions.

# Gavin Lake FVS-BC creative-silviculture state library

Full productive-AU run: **79 AUs, 474 FVS-BC cases, six treatments**.

This is the current Gavin Lake state-library evidence. It is not yet ingested as
a ws4 compiled matrix, and it is not a reviewed operational plan.

## Scope

- 79 productive AUs; AU 9999 (non-productive/unclassified) is excluded.
- 474 cases = 79 AUs x 6 treatments.
- 5,214 curve rows and 2,510,760 per-tree trajectory rows.
- 161,337 cut-list rows.
- 2009 LiDAR supplies piece size; the Williams Lake PSP supplies the BEC/age
  basal-area analog.
- All 79 AUs received a PSP target; mean target BA 45.5 m2/ha, mean initial BA
  45.6 m2/ha.

## Treatments

| ID | Prescription |
| --- | --- |
| `untreated` | no harvest |
| `ct60` | commercial thinning from below, residual 60% BA at year 0 |
| `fuel50` | fuel-mitigation thinning from below, residual 50% BA at year 0 |
| `selection80` | irregular selection, residual 80% BA in cycles 1, 3, 5, 7, 9 |
| `shelterwood40` | seed cut to 40% BA at year 0; final removal in cycle 4 |
| `vr20` | variable retention from above, residual 20% BA at year 0 |

FVS-BC reads the BC variant's `THINBBA`/`THINABA` basal-area targets in
**m2/ha**, not the imperial units in the US keyword guide. A target above the
standing BA is silently cancelled, so the targets are fractions of the initial
BA. The cycle field is one-based; cycle 4 schedules at year 30.

## Legacy comparison

`legacy_comparison.csv` compares the FVS-BC AU curves with the legacy clearcut
yield matrix:

- median difference between legacy yield at current age and FVS initial volume:
  **+18.1%**;
- median difference between legacy yield at current age + 100 and untreated FVS
  volume at year 100: **+69.1%**;
- 69 of 79 AUs have a legacy curve covering the current age; all 79 have a curve
  covering current age + 100.

The future difference is expected: the legacy curve is an 80-year clearcut
rotation while the FVS untreated case carries the current stand for 100 years
without harvest. This is a screening comparison, not a parity test.

## Outputs

- `curves.csv`: 5,214 FVS summary rows.
- `runs.csv`: 474 run records with AU, treatment, PSP target, density scale, and
  warnings.
- `comparison.csv`: initial, post-treatment, and final metrics.
- `cut_list.parquet`: 161,337 per-tree removals.
- `dbh_distribution.csv`: 5 cm DBH distributions by AU/treatment/year.
- `transitions.parquet`: ten-year live/harvest/mortality transitions.
- `legacy_comparison.csv` and `legacy_comparison_summary.json`.
- `tree_lists/`: the sampled LiDAR list for each AU.
- `tree_trajectories.parquet`: the full per-tree, per-period FVS output. It is
  generated locally and not committed (164 MB).

## Reproduce

```bash
python runbooks/build_gl_fvsbc_pilot.py --all-aus --workers 6
python runbooks/build_gl_fvsbc_transitions.py \
  --pilot-dir data/fvsbc/gl_all --out-dir data/fvsbc/gl_all
python runbooks/build_gl_fvsbc_legacy_comparison.py \
  --fvs-dir data/fvsbc/gl_all
```

The PSP extract is expected at `../../inv01-data/psp` relative to this
repository, or pass `--psp-dir`.

## ws4 state graph v0

`ws4_state_graph/` is a validated single-entry ws4 dataset:

- 79 AU fragments, 4,663.0 ha;
- 474 tracks and 395 treatment edges;
- 15,889 curves, including first- and second-entry harvest products and two-entry continuation tracks;
- `ws4 validate` accepted;
- baseline and CT60 schedules included.

100-year ws4 runs:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline | 3,100,745 m3 |
| CT60 once | 2,151,172 m3 |
| CT60 twice | 1,352,213 m3 |
| CT60 first-entry harvest | 466,183 m3 (443,393 sawlog + 22,789 pulp) |
| CT60 second-entry harvest | 463,830 m3 (460,558 sawlog + 3,272 pulp) |

This is a single-entry v0: AU-scale fragments, one treatment offset per AU, and
the FVS post-treatment cycle shifted back to the entry age. It is a valid
state graph and a runnable baseline, not a multi-entry selection matrix.

## Spatial graph

`ws4_spatial_graph/` is the age-binned spatial version:

- 1,505 productive fragments (1,402 AU-9999 fragments excluded);
- 3,016 tracks, 2,639 treatment edges, 75,677 curves;
- `ws4 validate` accepted;
- baseline 3,112,737 m3; CT60 twice 1,352,213 m3; harvest 930,013 m3.

## Cohort graph

`ws4_cohort_graph/` adds ten-year entry cohorts:

- 22,997 tracks, 22,620 treatment edges, 587,874 curves;
- a greedy one-thinning even-flow schedule;
- thinning even-flow of 46,618 m3 per decade;
- final-harvest even-flow of 184,796 m3 per decade on 618 blocks, final standing 1,156,523 m3 after planted regeneration;
- full liquidation of 214,789 m3 per decade.

The 184,796 m3 schedule is a 100-year liquidation, not a perpetual AAC.

## Second rotation

`data/fvsbc/gl_second_rotation/` tests the 184,796 m3 schedule against a planted
second rotation at age 80. The second rotation supports about **113,388
m3/decade**, not 185,000. The 185,000 figure is therefore a first-rotation
liquidation, not a sustained AAC.

## Limits

- The PSP analog is a regional BA/density correction, not a measured Gavin tree
  list.
- The 2009 canopy inventory is not a CFI. Species are VRI shares, DBH is height
  allometry, and crown ratio is fixed class 5.
- FVS-BC is uncalibrated for these AUs; the site index is a screening value.
- No regeneration, ingress, planting, fire, or climate extension is modelled.
- The state library still needs ingestion into the ws4 matrix contract and a
  full estate simulation. This folder is the source evidence, not the matrix.
- No legal or operational compliance claim is made.

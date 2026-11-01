# Gavin Lake FVS-BC creative-silviculture pilot

Six analysis units (AUs) from the 2025 VRI and the 2009 Gavin Lake tree
inventory, run through FVS-BC for an untreated baseline and five partial-harvest
prescriptions.

This is a pilot for the state-library design, not a full 80-AU rebuild and not a
reviewed operational plan.

## AUs

| AU | Area (ha) | VRI age | BEC | PSP BA (m2/ha) | PSP plots | Initial BA (m2/ha) | Initial TPH | Initial volume (m3/ha) |
| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 2 | 156.6 | 161.6 | ICHmk3 | 47.0 | 4 | 46.1 | 340 | 517 |
| 302 | 885.3 | 100.5 | ICHmk3 | 32.9 | 6 | 32.3 | 1,297 | 288 |
| 352 | 234.3 | 76.1 | ICHmk3 | 35.9 | 13 | 36.7 | 1,099 | 349 |
| 312 | 48.0 | 60.0 | ICHmk3 | 40.8 | 17 | 40.7 | 3,657 | 135 |
| 802 | 347.7 | 127.4 | SBSdw1 | 52.1 | 20 | 53.6 | 943 | 510 |
| 502 | 322.5 | 134.1 | SBSdw1 | 51.4 | 13 | 49.5 | 583 | 502 |

## Method

- Base tree list: 2009 FUSION LIDARBIN canopy inventory (`data/lidar/gavin_2009/`).
- DBH: height allometry. Crown ratio: fixed class 5. Species: assigned from the
  area-weighted 2025 VRI species shares.
- Density: the LiDAR list supplies piece size; total BA is scaled to a Williams
  Lake TSA PSP analog in the same BEC and an age window of +/-20 years.
- FVS-BC: 100 years, ten-year cycles, site species/index from the dominant AU
  species, and the fixed forest/habitat code used by the FVS-BC smoke case.
- The BC variant reads `THINBBA`/`THINABA` basal-area targets in **m2/ha**.
  Targets above the standing BA are quietly cancelled; all targets here are a
  fraction of the sampled initial BA.
- No regeneration, ingress, planting, fire, or climate extension is modelled.

## Treatments

| ID | Prescription |
| --- | --- |
| `untreated` | no harvest |
| `ct60` | commercial thinning from below, residual 60% BA at year 0 |
| `fuel50` | fuel-mitigation thinning from below, residual 50% BA at year 0 |
| `selection80` | irregular selection, residual 80% BA in cycles 1, 3, 5, 7, 9 (years 0, 20, 40, 60, 80) |
| `shelterwood40` | seed cut to 40% BA at year 0; final overstory removal in cycle 4 (year 30) |
| `vr20` | variable retention from above, residual 20% BA at year 0 |

## Final merchantable volume at year 100 (m3/ha)

| AU | untreated | ct60 | fuel50 | selection80 | shelterwood40 | vr20 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 758 | 505 | 423 | 531 | 20 | 276 |
| 302 | 518 | 298 | 223 | 352 | 19 | 296 |
| 352 | 659 | 489 | 395 | 414 | 22 | 378 |
| 312 | 538 | 541 | 495 | 404 | 31 | 457 |
| 802 | 739 | 500 | 392 | 561 | 19 | 380 |
| 502 | 507 | 310 | 253 | 420 | 40 | 230 |

The untreated rows are the no-harvest baseline. The partial-cut rows are not
meant to match the untreated final volume: they remove volume and leave a
different residual structure. `shelterwood40` ends with the overstory removed
and no regeneration model, so its final volume is near zero by construction.

## Outputs

- `curves.csv`: 36 runs x 11 periods of FVS summary metrics.
- `runs.csv`: run provenance, AU, treatment, sample, PSP BA, density scale, and
  warnings.
- `comparison.csv`: initial, post-treatment, and final metrics by AU/treatment.
- `cut_list.parquet`: per-tree removals.
- `dbh_distribution.csv`: DBH-class distributions by AU/treatment/year.
- `transitions.parquet`: ten-year DBH-class transitions with `live`, `harvest`,
  and `mortality` fates.
- `transitions_summary.json`: row counts and fate totals.
- `tree_lists/`: the sampled LiDAR lists used for each AU.
- `tree_trajectories.parquet`: the full per-tree, per-period FVS tree list. It is
  generated locally and not committed because it is large.

## Reproduce

```bash
python runbooks/build_gl_fvsbc_pilot.py
python runbooks/build_gl_fvsbc_transitions.py
```

The first command needs the PSP extract at `../../inv01-data/psp` relative to
this repository, or pass `--psp-dir`.

## Limits

- The PSP analog is a regional BA/density correction, not a measured Gavin tree
  list.
- The 2009 canopy inventory is not a CFI. Species are VRI shares, DBH is height
  allometry, and crown ratio is fixed.
- FVS-BC is uncalibrated for these AUs. The site index is a screening value.
- The six AUs are a pilot, not the full 80-AU estate.
- No legal or operational compliance claim is made.

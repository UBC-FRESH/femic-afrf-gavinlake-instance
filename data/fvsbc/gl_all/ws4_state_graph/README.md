# Gavin Lake FVS-BC ws4 state graph v0

A ws4-compatible, single-entry state graph compiled from the full FVS-BC AU
library.

## Contents

- 79 AU fragments, one per productive AU, area 4,663.0 ha.
- 474 tracks: untreated plus five treatments per AU.
- 395 treatment edges: untreated track to each treatment track at the AU age.
- 9,638 curve rows.
- `ws4 validate` accepts the dataset.
- Baseline and CT60 schedules are in `schedules/`.

## Build

```bash
python runbooks/build_gl_ws4_state_graph.py
ws4 validate --dataset ws4/runtime/fvsbc_state_graph
```

The committed dataset is the same table set copied from the runtime build.

## Simulation evidence

100-year ws4 runs on the same dataset:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline, no entry | 3,100,745 m3 |
| CT60 on all AUs at year 1 | 2,151,172 m3 |

The area remains 4,663.0 ha in both runs. The difference is the treatment track,
not an area change.

## What is exact

- The FVS curves, AU areas, ages, and treatment definitions are from
  `data/fvsbc/gl_all/`.
- The ws4 table contract is validated.
- The state transitions move a fragment from the untreated track to the
  treatment track.

## What is a v0 approximation

- **Single entry only.** A treatment edge carries one offset, the AU's entry
  age. Repeated selection entries need age-specific tracks.
- **AU-scale fragments.** The graph aggregates each AU into one fragment; it
  does not carry the 2,907 original spatial fragments.
- **Treatment curve shift.** The FVS post-treatment state is first observed in
  cycle 2 (year 10). The graph shifts that state back to the entry age.
- **No harvest products.** The graph carries yield and area features; it does
  not yet compile cut volume, sort, or delivered-wood products.
- **No regeneration.** The FVS runs have no regeneration, ingress, planting,
  fire, or climate extension.

This is a valid ws4 state graph and a runnable baseline. It is not yet the
full multi-entry creative-silviculture matrix.

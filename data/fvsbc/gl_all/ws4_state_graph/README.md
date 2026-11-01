# Gavin Lake FVS-BC ws4 state graph v1

A ws4-compatible **two-entry** state graph compiled from the full FVS-BC AU
library and the second-entry FVS chain.

## Contents

- 79 AU fragments, one per productive AU, area 4,663.0 ha.
- 632 tracks: untreated, five first-entry treatments, and the first two-entry
  continuation tracks.
- 553 treatment edges.
- 15,415 curves.
- 1,659 product rows.
- `ws4 validate` accepts the dataset.
- Baseline, one-entry, and two-entry schedules are in `schedules/`.

## Simulation evidence

100-year ws4 runs on the same dataset:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline, no entry | 3,100,745 m3 |
| CT60 once | 2,151,172 m3 |
| CT60 twice | 1,257,706 m3 |

The first CT60 entry produces 466,183 m3 of harvest (443,393 sawlog, 22,789
pulp). The second-entry harvest products are not yet compiled.

## What is exact

- The FVS curves, AU areas, ages, and treatment definitions are from
  `data/fvsbc/gl_all/`.
- The second-entry tracks are chained from the FVS year-10 post-treatment tree
  list in `data/fvsbc/gl_multientry/`.
- The ws4 table contract is validated.

## What is still approximate

- **AU-scale fragments.** The graph aggregates each AU into one fragment; it
  does not carry the 2,907 original spatial fragments.
- **Two entries only.** The graph carries one follow-up entry ten years after
  the first treatment.
- **Second-entry products are not compiled.** The second-entry cut list is not
  yet in the product curves.
- **Treatment curve shift.** The first-entry post-treatment state is first
  observed in cycle 2; the graph shifts it back to the entry age.
- **Simple product split.** Sawlog/pulp uses a 20 cm DBH threshold; grade, mill,
  and delivered-wood routing are not compiled.
- **No regeneration.** No regeneration, ingress, planting, fire, or climate
  extension.

This is a valid two-entry ws4 graph, but still not the final multi-entry
spatial matrix.

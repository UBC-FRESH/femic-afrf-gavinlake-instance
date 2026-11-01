# Gavin Lake FVS-BC ws4 state graph v1

A ws4-compatible **two-entry** state graph compiled from the full FVS-BC AU
library and the second-entry FVS chain.

## Contents

- 79 AU fragments, one per productive AU, area 4,663.0 ha.
- 632 tracks: untreated, five first-entry treatments, and the first two-entry
  continuation tracks.
- 553 treatment edges.
- 15,889 curves.
- 2,133 product rows, including first- and second-entry total, sawlog, and pulp
  harvest.
- `ws4 validate` accepts the dataset.
- Baseline and two-entry schedules are in `schedules/`.

## Simulation evidence

100-year ws4 runs on the same dataset:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline, no entry | 3,100,745 m3 |
| CT60 once | 2,151,172 m3 |
| CT60 twice | 1,352,213 m3 |

CT60 harvest:

| Entry | Total | Sawlog | Pulp |
| --- | ---: | ---: | ---: |
| first | 466,183 m3 | 443,393 | 22,789 |
| second | 463,830 m3 | 460,558 | 3,272 |
| total | 930,013 m3 | 903,951 | 26,062 |

## What is exact

- The FVS curves, AU areas, ages, and treatment definitions are from
  `data/fvsbc/gl_all/`.
- The second-entry tracks are chained from the FVS year-10 post-treatment tree
  list in `data/fvsbc/gl_multientry/`.
- Harvest volume is `MCuM x TPH` from the first- and second-entry cut lists;
  sawlog is DBH >= 20 cm.
- The ws4 table contract is validated.

## What is still approximate

- **AU-scale fragments.** The graph aggregates each AU into one fragment; it
  does not carry the 2,907 original spatial fragments.
- **Two entries only.** The graph carries one follow-up entry ten years after
  the first treatment.
- **Treatment curve shift.** The first-entry post-treatment state is first
  observed in cycle 2; the graph shifts it back to the entry age.
- **Simple product split.** Sawlog/pulp uses a 20 cm DBH threshold; grade, mill,
  and delivered-wood routing are not compiled.
- **No regeneration.** No regeneration, ingress, planting, fire, or climate
  extension.

This is a valid two-entry ws4 graph, but still not the final multi-entry
spatial matrix.

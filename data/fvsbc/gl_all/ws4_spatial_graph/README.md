# Gavin Lake FVS-BC spatial ws4 graph

The age-binned spatial version of the two-entry FVS-BC state graph.

## Contents

- **1,505 productive fragments** across **1,505 blocks** and 4,663.0 ha.
- The 2,907-fragment legacy inventory includes 1,402 AU-9999 fragments; those
  are non-productive/unclassified and are excluded here.
- **3,016 tracks**: one untreated track per AU and 10-year age bin, plus
  first-entry and second-entry treatment tracks.
- **2,639 treatment edges**.
- **75,677 curves**.
- **7,917 product rows**.
- `ws4 validate` accepts the dataset.
- Baseline and CT60-twice schedules are in `schedules/`.

## Fragments and age bins

Each fragment keeps its own `fragment_id`, `block_id`, area, and age. It is
assigned to the untreated track for its AU and 10-year age bin. The FVS curve is
shifted from the AU entry age to the bin age, so a young fragment does not
inherit the AU's current volume.

## Simulation evidence

100-year runs:

| Run | Final feature volume at 2099 |
| --- | ---: |
| baseline | 3,112,737 m3 |
| CT60 twice | 1,352,213 m3 |

CT60 twice harvest: **930,013 m3** total — 903,951 sawlog and 26,062 pulp.

## What is exact

- Fragment identity, block, area, and age are from the VRI/legacy spatial layer.
- FVS curves, treatment definitions, and cut products are from
  `data/fvsbc/gl_all/` and `data/fvsbc/gl_multientry/`.
- The ws4 table contract is validated.
- Treatment edges are per age bin, so a fragment is treated at its own age.

## What is still approximate

- **10-year age bins.** Fragments within a bin share the shifted AU curve.
- **Two entries only.**
- **Curve shift, not a distinct FVS run per bin.** The FVS run is per AU, not per
  fragment or bin.
- **No regeneration, fire, or climate extension.**
- **Simple product split.** 20 cm DBH sawlog threshold; no grade, mill, or
  delivered-wood routing.

This is the first spatial ws4 graph with age-appropriate treatment timing. It is
not yet a per-fragment FVS simulation.

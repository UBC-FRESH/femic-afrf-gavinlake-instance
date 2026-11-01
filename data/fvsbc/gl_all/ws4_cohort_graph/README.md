# Gavin Lake FVS-BC entry-age cohort graph

Spatial cohort graph with first-cut entries through 180 years and planted
second-rotation tracks.

- **1,505 productive fragments**, 4,663.0 ha
- **26,390 tracks**
- **26,013 treatment edges**
- **672,699 curves**
- **78,039 product rows**
- entry offsets **0, 10, ..., 180 years**
- `ws4 validate` passes

## 200-year result

The all-block first-plus-second rotation schedule has a mean of **172,609
m3/decade**, but ranges from **0 to 241,519 m3/decade**. It is not an even flow.
A target-150,000 greedy schedule selects 308 blocks and still averages only
112,709 m3/decade.

**185,000 m3/decade is not sustained on this land base.**

## Files

- `schedules/evenflow.csv` — thinning-only flow
- `schedules/evenflow_aac.csv` — all-block final harvest
- `schedules/evenflow_ltsy.csv` — 176,000-target greedy final harvest
- `summary.json`

## Limits

- 10-year age bins and shifted FVS curves
- planted bare-ground second rotation, not natural ingress
- no fire, climate, grade, mill, or delivered-wood routing
- greedy schedules, not a joint first/second optimizer

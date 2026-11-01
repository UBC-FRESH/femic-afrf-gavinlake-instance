# Gavin Lake FVS-BC second-entry chain

79 AUs x 2 first-entry treatments, re-run from the FVS year-10 post-treatment
tree list.

## Result

- 158 second-entry runs
- 1,738 summary rows
- median difference between first-entry post-treatment volume and second-entry
  initial volume: **+3.8%**
- median second-entry growth over 100 years: **+72.5 m3/ha**
- second-entry cut list: 389 KB parquet

## Method

For each AU and first treatment (`ct60`, `selection80`):

1. take the FVS year-10 tree list;
2. remove the trees named in the first-entry cut list;
3. regroup the remaining trees by `TreeId`;
4. run FVS-BC for the next 100 years with the same treatment.

The tree list is sampled, so the second-entry initial BA can differ slightly
from the first-entry summary.

## Files

- `second_entry_curves.csv`
- `second_entry_runs.csv`
- `second_entry_cuts.parquet`
- `comparison.csv`
- `summary.json`

## Limits

- Two FVS cases chained, not one continuous projection.
- Same AU site code retained.
- No regeneration, ingress, planting, fire, or climate extension.

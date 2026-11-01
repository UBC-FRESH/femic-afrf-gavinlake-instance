# Gavin Lake FVS-BC second-entry chain

79 AUs x 2 first-entry treatments, re-run from the FVS year-10 post-treatment
tree list.

## Result

- 158 second-entry runs
- 1,738 summary rows
- median difference between the first-entry post-treatment volume and the
  second-entry initial volume: **-0.9%**
- median second-entry growth over 100 years: **+71.5 m3/ha**
- The second entry is a new FVS case, not a continuous single projection.

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
- `comparison.csv`
- `summary.json`

## Limits

- Two FVS cases chained, not one continuous projection.
- Same AU site code retained.
- No regeneration, ingress, planting, fire, or climate extension.
- Second-entry cut volume is not yet compiled into ws4 products.

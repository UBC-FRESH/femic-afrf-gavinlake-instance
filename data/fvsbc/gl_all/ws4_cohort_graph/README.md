# Gavin Lake FVS-BC entry-age cohort graph

A spatial cohort graph for ten-year scheduling. Every AU/10-year age bin has an
untreated track, five treatment tracks at every entry offset, and a clearcut
final-harvest track at every entry offset.

## Contents

- **1,505 productive fragments**, 4,663.0 ha.
- **22,997 tracks**.
- **22,620 treatment edges**.
- **1,266,474 curves**.
- **67,860 product rows**.
- entry offsets **0, 10, 20, ..., 90 years**.
- `ws4 validate` accepts the dataset.

## Even-flow schedules

### Thinning only

`schedules/evenflow.csv` assigns one `CT60` thinning per block. It produces
**46,618 m3 per decade**, flat to about 1 m3.

This is not an AAC: it has no final harvest.

### Final harvest, all blocks

`schedules/evenflow_aac.csv` assigns one clearcut per block across the ten
periods. It produces **214,789 m3 per decade**, flat.

All 1,505 blocks are harvested; final standing volume is zero.

### Final harvest near the LTSY target

`schedules/evenflow_ltsy.csv` selects 618 blocks and leaves 887 standing. It
produces:

| Period | Harvest (m3) |
| ---: | ---: |
| 0 | 184,800 |
| 10 | 184,798 |
| 20 | 184,798 |
| 30 | 184,799 |
| 40 | 184,797 |
| 50 | 184,795 |
| 60 | 184,797 |
| 70 | 184,793 |
| 80 | 184,795 |
| 90 | 184,789 |

Total: **1,847,961 m3**. Final standing volume: **438,394 m3**.

This is within 0.1% of the 185,000 m3 first-guess LTSY target and is flat to
11 m3 per decade.

## What the clearcut cohort is

A clearcut entry is a final harvest at the entry age:

- harvest volume is the standing merchantable volume at that age;
- sawlog is DBH >= 20 cm; the rest is pulp;
- post-harvest feature yield is zero;
- there is no regeneration, ingress, or planting.

## Limits

- The 184,796 m3 schedule is a **100-year liquidation**, not a perpetual AAC.
  The final 438,394 m3 is the unharvested inventory.
- 10-year age bins and shifted FVS curves.
- No regeneration, fire, or climate extension.
- No grade, mill, or delivered-wood routing.
- The clearcut yield is the standing volume at entry, not an FVS post-harvest
  regeneration projection.

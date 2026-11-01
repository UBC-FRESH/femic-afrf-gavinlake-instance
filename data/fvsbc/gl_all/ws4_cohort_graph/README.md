# Gavin Lake FVS-BC entry-age cohort graph

A spatial cohort graph for ten-year scheduling. Every AU/10-year age bin has an
untreated track, five treatment tracks at every entry offset, and a clearcut
final-harvest track at every entry offset. The clearcut track enters a planted
bare-ground FVS regeneration curve.

## Contents

- **1,505 productive fragments**, 4,663.0 ha.
- **22,997 tracks**.
- **22,620 treatment edges**.
- **587,874 curves**.
- **67,860 product rows**.
- entry offsets **0, 10, 20, ..., 90 years**.
- `ws4 validate` accepts the dataset.

## Even-flow schedules

### Thinning only

`schedules/evenflow.csv` assigns one `CT60` thinning per block. It produces
**46,618 m3 per decade**, flat to about 1 m3.

### Final harvest, all blocks

`schedules/evenflow_aac.csv` assigns one clearcut per block across the ten
periods. It produces **214,789 m3 per decade**, flat. Every clearcut enters a
planted regeneration track.

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

Total: **1,847,961 m3**. Final standing volume after planted regeneration:
**1,156,523 m3**.

This is within 0.1% of the 185,000 m3 first-guess LTSY target and flat to
11 m3 per decade.

## Clearcut and regeneration

- harvest volume is the standing merchantable volume at entry;
- sawlog is DBH >= 20 cm; the rest is pulp;
- the post-harvest track is a planted bare-ground FVS regeneration curve;
- there is no natural ingress, brushing, or competition control.

## Limits

- The 184,796 m3 schedule is a **100-year liquidation**, not a perpetual AAC.
  The final 1,156,523 m3 includes planted second-rotation growth on harvested
  blocks; it is not a second harvest.
- 10-year age bins and shifted FVS curves.
- No fire or climate extension.
- No grade, mill, or delivered-wood routing.
- Clearcut yield is the standing volume at entry; regeneration is a separate
  bare-ground FVS case, not a continuous projection.

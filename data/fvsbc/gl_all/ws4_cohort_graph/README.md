# Gavin Lake FVS-BC entry-age cohort graph

A spatial cohort graph for ten-year scheduling. Every AU/10-year age bin has an
untreated track, treatment tracks at entry offsets through 90 years, and
clearcut tracks at entry offsets through 180 years. Clearcut entries enter a
planted bare-ground FVS regeneration curve.

## Contents

- **1,505 productive fragments**, 4,663.0 ha.
- **23,374 tracks**.
- **22,997 treatment edges**.
- **597,299 curves**.
- **68,991 product rows**.
- entry offsets **0, 10, ..., 180 years**.
- `ws4 validate` accepts the dataset.

## One-rotation schedules

| Schedule | Harvest per decade |
| --- | ---: |
| thinning only, `evenflow.csv` | 46,618 m3 |
| all-block final harvest, `evenflow_aac.csv` | 214,789 m3 |
| LTSY-target final harvest, `evenflow_ltsy.csv` | 184,796 m3 |

The LTSY schedule harvests 618 blocks, leaves 887 standing, and is flat to
11 m3 per decade. It is a 100-year liquidation, not a perpetual AAC.

## 200-year test

`data/fvsbc/gl_second_rotation/schedule_200_year.csv` adds the planted second
rotation at age 80.

- all-block mean: **172,609 m3/decade**
- minimum: **0 m3/decade**
- maximum: **241,519 m3/decade**
- target-150,000 greedy: 308 blocks, mean **112,709 m3/decade**, late periods
  underfilled

The 200-year mean is not an even flow. The first cuts are now available through
180 years, but the second cuts beyond 200 fall outside the horizon and the
greedy schedule does not hold a flat target.

## Conclusion

185,000 m3/decade is not sustained on this land base with the current planted
regeneration and cohort structure. A defensible AAC requires either a lower
target, more land, more intensive regeneration, or a formal multi-period
optimizer that treats first and second cuts jointly.

## Limits

- 10-year age bins and shifted FVS curves.
- Second rotation is a planted bare-ground FVS curve at age 80.
- No natural ingress, brushing, competition control, fire, or climate extension.
- No grade, mill, or delivered-wood routing.

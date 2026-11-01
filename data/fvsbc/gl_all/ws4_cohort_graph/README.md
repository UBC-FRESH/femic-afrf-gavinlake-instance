# Gavin Lake FVS-BC entry-age cohort graph

A spatial cohort graph for ten-year even-flow scheduling. Every AU/10-year age
bin has one untreated track and one track for every treatment and entry offset
(0, 10, 20, ..., 90 years).

## Contents

- **1,505 productive fragments**, 4,663.0 ha.
- **19,227 tracks**.
- **18,850 treatment edges**.
- **493,624 curves**.
- **56,550 product rows**.
- `ws4 validate` accepts the dataset.

## Even-flow thinning schedule

`schedules/evenflow.csv` assigns one `CT60` entry per block to the least-loaded
decade. 1,478 blocks are treated; the remaining blocks have no positive CT60
cut in their bin.

Estimated and simulated ten-year harvest:

| Period (years) | Harvest (m3) |
| ---: | ---: |
| 0 | 46,618 |
| 10 | 46,618 |
| 20 | 46,618 |
| 30 | 46,618 |
| 40 | 46,619 |
| 50 | 46,618 |
| 60 | 46,619 |
| 70 | 46,618 |
| 80 | 46,619 |
| 90 | 46,618 |

The simulated period totals match the greedy estimates to the cubic metre. The
schedule is a thinning flow, not a complete AAC: every block receives one
commercial thinning and no final harvest or regeneration. The 100-year final
standing volume is 1,815,758 m3.

## Why this is not the AAC yet

The legacy LTSY target is 185,000 m3 per ten-year period. This graph sustains
about **46,600 m3** per period from one thinning per block. It does not include
a final clearcut or shelterwood removal, so it cannot be compared directly with
the legacy 80-year clearcut AAC.

## Limits

- One entry per block; no repeated selection sequence.
- 10-year age bins and shifted FVS curves.
- CT60 only in the even-flow schedule; the other treatment cohorts exist but are
  not used in this schedule.
- No regeneration, fire, or climate extension.
- No grade, mill, or delivered-wood routing.

## Files

- `schedules/evenflow.csv`
- `schedules/evenflow.json`
- `summary.json`

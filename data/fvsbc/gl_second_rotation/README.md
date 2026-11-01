# Gavin Lake second-rotation test

Does the 184,796 m3/decade first-rotation flow survive a second rotation?

**No.** The planted second rotation supports about **113,388 m3/decade**, not
185,000.

## Method

- Take the 618 blocks harvested by `evenflow_ltsy.csv`.
- Use each block's AU planted regeneration curve at age 80.
- Assign the second harvest to the period 80 years after the first entry.
- Do not schedule a second cut or add natural regeneration.

## Result

- first rotation: **184,796 m3/decade**
- second rotation: **113,388 m3/decade**
- second-rotation total: **1,133,877 m3**
- second-rotation area: **4,000.0 ha**

By period:

| Period | Second-rotation volume (m3) |
| ---: | ---: |
| 80 | 153,797 |
| 90 | 155,694 |
| 100 | 132,302 |
| 110 | 117,305 |
| 120 | 111,101 |
| 130 | 103,900 |
| 140 | 95,057 |
| 150 | 93,232 |
| 160 | 90,685 |
| 170 | 80,804 |

The overlap at periods 80-90 is because the first-rotation entries were spread
across all ten decades.

## Interpretation

The 185,000 m3 first-rotation number is a **liquidation AAC**, not a sustained
AAC. A second rotation on the same 4,000 ha cannot replace it.

To sustain 185,000 m3/decade, the model needs one or more of:

- a lower AAC, near **113,000 m3/decade** on this land base;
- more productive area;
- a shorter or more productive regeneration pathway;
- more intensive silviculture;
- a different land-base assumption.

## Limits

- second rotation is the planted FVS curve at age 80, not a scheduled harvest;
- only blocks harvested in the first rotation are counted;
- no natural ingress, brushing, competition control, fire, or climate change;
- no second-rotation sorting, haul, or mill constraints.

## Files

- `second_rotation.csv`
- `second_rotation_by_period.csv`
- `summary.json`

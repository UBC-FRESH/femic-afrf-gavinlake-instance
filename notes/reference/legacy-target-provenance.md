# The 500,000 harvest target: what the archive records and what it does not

Date: 2026-10-26
Status: target-interpretation correction

## The literal

The AFRF H scenario script contains:

```text
data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh:13
setMinimumPeriodic("product.yield.managed.total", 500000, 1, 30);
```

The same scenario sets the harvest target to a linear penalty:

```text
line 15
control.getTarget("product.yield.managed.total").setLinear(true);
```

and then pairs it with an even-flow target on the same underlying harvest
account:

```text
lines 28-32
setActive("product.flow.yield.even", true, true, true);
setMinimumPeriodic("product.flow.yield.even", -1, 1, 30);
setMinWeight("product.flow.yield.even", 1000, 1, 30);
setMaximumPeriodic("product.flow.yield.even", 1, 1, 30);
setMaxWeight("product.flow.yield.even", 1000, 1, 30);
```

## What the archive does not record

The archive does not record the modeler's intent for the 500,000 value. It does
not say whether the value is:

- a deliberately unattainable minimum used to pull harvest levels up across
  all periods;
- a calibrated feasible floor;
- a template value inherited from another model; or
- an exploratory value from a scenario run.

That intent is the modeler's. It cannot be recovered from the number alone.

## Why an unattainable minimum is a legitimate choice

In Patchworks, a minimum target can be set deliberately above the feasible
level. With a linear penalty shape, the target then acts as a pull-up term:
every period contributes a penalty until harvest rises, while the even-flow
target controls the shape of the resulting profile. This is a standard
wood-supply modelling technique. The AFRF scenario's combination of
`setLinear(true)` on `product.yield.managed.total` and an even-flow target on
`product.flow.yield.even` is consistent with that use.

Consistency is not proof. Only the modeler can say whether that was the intent.

## Provenance observations

These are factual observations, not a conclusion about intent:

- The same literal appears in the MKRF legacy target
  `data/legacy_mkrf/compiled_controls/targets/01_harvest.bsh`.
- The AFRF package's `00_Build_Matrix.bsh` and `01_Topology_fragments.bsh`
  still point at `S:\1034\13\04_Models\PW_MKRF\...`.
- The MKRF legacy `initialTargetSummary.csv` records a 500,000 target and
  achieved values around 350,000–363,000 m³ per period.
- The MKRF ws4 translation describes the 500,000 floor as infeasible for its
  4,810 ha model.

These observations suggest shared ancestry. They do not establish that the
AFRF value is a copy, a template, or a deliberate pull-up target. Those are
different claims, and the archive settles none of them.

## The calibrated-looking value

The same scenario sets:

```text
line 19
setMinimumPeriodic("feature.yield.managed.total", 1277067, 30, 30);
```

with the comment "set growing stock constraints- AFRF (90 percent of initial
GS)". The measured initial growing stock is 1,418,962.31 m³; 90 percent is
1,277,066.08 m³, within 1 m³ of the literal. That is strong evidence that this
value is tied to the Gavin Lake matrix. Whether it is a hard policy floor or a
scenario choice is still the modeler's call.

## How to report the baseline

The Phase 1 baseline does not meet the 500,000 literal. That is a factual
result. It is **not** evidence that:

- the target was wrong;
- the target was not calibrated;
- the modeler intended a feasible floor; or
- an AFRF harvest policy is infeasible.

If the 500,000 is a pull-up target, the baseline's shortfall is expected. The
useful evidence is the harvest trajectory, the growing-stock trajectory, and
the target penalties, not a verdict on the target.

## A defensible first guess

The instance now derives a first-guess periodic target from the compiled
matrix rather than from the literal. `ws4/estimate_ltsy_target.py`:

1. builds an area-weighted mean yield curve from the current track curves;
2. finds the culmination of mean annual increment (CMAI);
3. multiplies by the THLB area;
4. multiplies by the ten-year period width; and
5. multiplies by 1.1 for a slightly-too-high first guess.

On the productive THLB proxy (`CONTCLAS = C`, 4,662.96 ha), the CMAI is
3.599653 m³/ha/yr at age 100. LTSY is 16,785.06 m³/yr, or 167,850.57 m³ per
ten-year period. The ×1.1 first guess is 184,635.63 m³, rounded to 185,000.

`ws4/targets_gavin_ltsy.yaml` is the runnable target. The baseline mean of
188,677.89 m³ is about 2.2 percent above it, and the baseline meets 185,000 m³
in 22 of 30 periods. The 1,277,067 m³ growing-stock target is the binding
constraint. The evidence is in `ws4/evidence/ltsy/`.

## Recommendation

1. Use `ws4/targets_gavin_ltsy.yaml` as the first runnable target.
2. Keep the literal 500,000 in `ws4/targets_legacy_harvest.yaml` as a parity
   reference and possible pull-up target.
3. Ask the modeler or AFRF staff what the 500,000 was intended to do before
   replacing it or optimizing against it.
2. Keep the literal in a clearly named parity file so the scenario can be
   reproduced.
3. Report the baseline as a trajectory and target-status table, not as a
   judgment on the target's validity.
4. If a feasible floor is wanted, derive it from the matrix or from a reviewed
   AFRF policy statement, and record the basis.

## Reproduce

```bash
grep -n "500000\|setLinear\|product.flow.yield.even" \
  data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh
```

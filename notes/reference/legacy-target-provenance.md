# Provenance of the 500,000 harvest floor

Date: 2026-10-26
Status: correction to the Phase 1 framing

## Question

Where did the `500000` in
`data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh` come from, and is it a
calibrated AFRF/Gavin Lake target?

## Short answer

It is a literal in the AFRF scenario script:

```text
setMinimumPeriodic("product.yield.managed.total", 500000, 1, 30);
```

at `scenarios_AFRF_H.bsh:13`. But it is **not** AFRF-calibrated. It is a copied
MKRF legacy template/aspirational floor. Treat it as a parity reference, not as
an approved Gavin Lake policy target.

## Evidence

### 1. The AFRF package's build scripts still point at MKRF

The archive's `AFRF/scripts/00_Build_Matrix.bsh` and
`AFRF/scripts/01_Topology_fragments.bsh` both use paths under
`S:\1034\13\04_Models\PW_MKRF\...`, not AFRF paths. The build scripts were
copied from the MKRF package and not fully retargeted. Their archive entries and
dispositions are in `metadata/legacy_archive_inventory.csv`.

### 2. The target line is identical to the MKRF legacy target

The MKRF legacy target file has the same statement:

```text
setActive ("product.yield.managed.total", true, true, false); setMinimumPeriodic ("product.yield.managed.total", 500000, 1, 30); setMinWeight ("product.yield.managed.total", 1, 1, 30);
```

Source: `UBC-FRESH/femic-mkrf-instance`,
`data/legacy_mkrf/compiled_controls/targets/01_harvest.bsh`.

The AFRF script changes the output path and the carbon setting, but the harvest
floor is the same round number.

### 3. The MKRF legacy model did not meet it either

The MKRF `models/mkrf_patchworks_model_poc/analysis/initialTargetSummary.csv`
records a 500,000 target and achieved values around 350,000–363,000 m³ per
period. The 500,000 was an aspirational floor in the legacy MKRF run, not a
met constraint.

The MKRF ws4 translation says so explicitly:

- `ws4/targets_legacy.yaml`: "the literal legacy 500,000 m3/decade floor ... is
  not expected to be feasible for the current 4,810 ha MKRF model."
- `ws4/targets.yaml`: the 4,810 ha model uses 300,000 m³/decade, "which is in
  the range produced by the translated spatially constrained baseline."

### 4. The growing-stock floor is AFRF-calibrated; the harvest floor is not

The same scenario sets:

```text
setMinimumPeriodic("feature.yield.managed.total", 1277067, 30, 30);
```

with the comment "set growing stock constraints- AFRF (90 percent of initial
GS)". The compiled Gavin Lake matrix has an initial growing stock of
1,418,962.31 m³. Ninety percent is 1,277,066.08 m³, within 1 m³ of the
1,277,067 literal. That target **is** calibrated to the Gavin Lake matrix.

The 500,000 harvest floor has no equivalent AFRF-specific derivation. It is a
round number inherited from the MKRF template.

### 5. The N variant shows copy-paste experimentation

`scenarios_AFRF_N.bsh` differs from the H variant mainly in output paths and one
carbon-stock floor (`150000000` instead of `15000000`). That is consistent with
a copied scenario set being edited for a run, not a reviewed policy package.

## Conclusion

- The **500,000 m³ per ten-year period** floor is a **copied legacy template
  value**, not a calibrated Gavin Lake target. It is useful as a parity
  reference and as a stress test. It should not be described as an AFRF policy
  requirement.
- The **1,277,067 m³ growing-stock floor at period 30** is **calibrated** to
  this matrix (90 percent of measured initial growing stock) and should remain
  the primary structural benchmark.
- The Phase 1 baseline finding is therefore narrower and more useful than the
  first framing: a sustained 80-year clearcut rotation on this matrix produces
  about 189,000 m³ per decade, which is far below the copied 500,000 floor. That
  is a statement about the copied floor and the compiled matrix, not about an
  approved AFRF harvest target.

## Recommendation

1. Keep the literal 500,000 target in a clearly named parity file, for
   comparison with the legacy script.
2. Do not use 500,000 as the runnable Gavin Lake harvest target unless AFRF
   confirms it is the intended policy value and the landbase/unit basis is
   reconciled.
3. Build the next runnable target set around:
   - the calibrated 1,277,067 m³ growing-stock floor;
   - a harvest level derived from the compiled matrix or confirmed by AFRF
     staff; and
   - the even-flow shape, with a stated reference period.
4. If a 500,000 floor is confirmed, record the unit, landbase, treatment set,
   and rotation that make it feasible; the compiled matrix alone does not.

## Reproduce

```bash
# The AFRF literal
grep -n "500000" data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh

# The MKRF legacy literal
grep -n "500000" \
  ../femic-mkrf-instance/data/legacy_mkrf/compiled_controls/targets/01_harvest.bsh
```

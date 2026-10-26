# Legacy scenario catalog

`legacy_catalog.yaml` records all nine scenarios in
`data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh` and their translation
status.

## Status values

- `translated` — a ws4 target file exists and can be read by `ws4 optimize` or
  `ws4 report`.
- `deferred` — the target is recorded, but the account or the input it needs is
  not in the compiled matrix. The reason is in the catalog.
- `rejected` — the target is not modelled, with a reason.

## Current status

| Scenario | Objective | Status |
| --- | --- | --- |
| `scenario_01` | Maximize timber harvest | translated to `ws4/targets_legacy_harvest.yaml` |
| `scenario_02` | Carbon stocks, HWP 0 | deferred |
| `scenario_03` | Carbon stocks, HWP 50 | deferred |
| `scenario_04` | Carbon stocks, HWP 100 | deferred |
| `scenario_05` | Carbon stocks, half-life | deferred |
| `scenario_06` | Carbon sequestration, HWP 0 | deferred |
| `scenario_07` | Carbon sequestration, HWP 50 | deferred |
| `scenario_08` | Carbon sequestration, HWP 100 | deferred |
| `scenario_09` | Carbon sequestration, half-life | deferred |

## Why the carbon scenarios are deferred

The legacy pin creates the carbon stock and flux accounts at runtime:

- `control.duplicateAccount` builds `feature.carbon.managed.total.stock.0`,
  `.50`, `.100`, and `.half` from a base `.es` account and the product HWPS
  stock.
- `control.addFlowValueAccount` builds `feature.carbon.managed.total.flux.*`
  from those stock accounts.

The compiled matrix does not contain the duplicates or the aggregate `.es`
account. The `.es` account in `accounts.csv` is an aggregation over 28 carbon
feature accounts; ws4's simulator reports the source feature accounts, not the
runtime aggregate. The target units are also unresolved: the scenario floor is
15,000,000 while the sum of the compiled carbon pools at offset -1 is about
2,747,522.

Do not run these scenarios as if they were translated. A future task can add a
derived-account layer and settle the units from the original XML or workbook.

## Adding a translated scenario

1. Add the target file under `ws4/`.
2. Replace the scenario's `status: deferred` with `status: translated` and set
   `target_file`.
3. Keep the source line numbers.
4. Run `ws4 report --targets <file>` and record the result in the evidence.

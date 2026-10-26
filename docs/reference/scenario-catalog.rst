Scenario Catalog
================

Source
------

``data/legacy_gavinlake/scripts/scenarios_AFRF_H.bsh`` defines nine scenarios.
Every scenario starts from the same base:

- ``clearTargets()`` and ``control.cancelTreatments()``;
- a growing-stock floor of 1,277,067 m³ at period 30;
- a bounded even-flow ratio between -1 and 1 with weight 1000; and
- an ``analyze`` call with 50,000 iterations and a default improvement of 0.05.

The difference between scenarios is the active objective and its floor. The
machine-readable disposition is in ``ws4/scenarios/legacy_catalog.yaml``.

Target interpretation
---------------------

The 500,000 m³ harvest target in ``scenario_01`` is a literal scenario
parameter. The archive does not record the modeler's intent. In Patchworks, an
unattainable minimum with a linear penalty can be a deliberate pull-up
technique, especially when paired with an even-flow target. The AFRF scenario
sets a linear penalty and pairs the harvest target with an even-flow target,
which is consistent with that use but does not prove it. See
``notes/reference/legacy-target-provenance.md``.

Runnable target
---------------

The runnable first guess is ``ws4/targets_gavin_ltsy.yaml``. It is derived from
the area-weighted mean yield curve: CMAI 3.599653 m³/ha/yr at age 100 on the
4,662.96 ha productive THLB proxy, LTSY 16,785.06 m³/yr, 167,850.57 m³ per
ten-year period, and a ×1.1 first guess of 184,635.63 m³, rounded to 185,000.
The baseline meets that level in 22 of 30 periods. The literal 500,000 remains
in ``ws4/targets_legacy_harvest.yaml`` as a parity reference.

Catalog
-------

.. list-table::
   :header-rows: 1
   :widths: 14 36 32 18

   * - ID
     - Objective
     - Legacy target
     - Status
   * - ``scenario_01``
     - Maximize timber harvest
     - ``product.yield.managed.total`` >= 500,000 m³
     - translated
   * - ``scenario_02``
     - Maximize carbon stocks, HWP emission 0
     - ``feature.carbon.managed.total.stock.0`` >= 15,000,000
     - deferred
   * - ``scenario_03``
     - Maximize carbon stocks, HWP emission 50
     - ``feature.carbon.managed.total.stock.50`` >= 15,000,000
     - deferred
   * - ``scenario_04``
     - Maximize carbon stocks, HWP emission 100
     - ``feature.carbon.managed.total.stock.100`` >= 15,000,000
     - deferred
   * - ``scenario_05``
     - Maximize carbon stocks, half-life
     - ``feature.carbon.managed.total.stock.half`` >= 15,000,000
     - deferred
   * - ``scenario_06``
     - Maximize carbon sequestration, HWP emission 0
     - ``feature.carbon.managed.total.flux.0`` >= 15,000,000
     - deferred
   * - ``scenario_07``
     - Maximize carbon sequestration, HWP emission 50
     - ``feature.carbon.managed.total.flux.50`` >= 15,000,000
     - deferred
   * - ``scenario_08``
     - Maximize carbon sequestration, HWP emission 100
     - ``feature.carbon.managed.total.flux.100`` >= 15,000,000
     - deferred
   * - ``scenario_09``
     - Maximize carbon sequestration, half-life
     - ``feature.carbon.managed.total.flux.half`` >= 15,000,000
     - deferred

The N variant differs in one carbon-stock floor and in its output paths. Its
matrix is incomplete, so it is not a runnable second scenario set.

Phase 1 disposition
-------------------

- ``scenario_01`` is translated into ``ws4/targets_legacy_harvest.yaml``.
- ``scenario_02`` through ``scenario_09`` are deferred. The compiled matrix
  does not carry the runtime duplicate stock/flux accounts that the pin creates
  with ``control.duplicateAccount`` and ``control.addFlowValueAccount``. The
  base ``feature.carbon.managed.total.stock.es`` account is an aggregation
  over 28 carbon features, and ws4 reports the source features rather than the
  runtime aggregate. The target units are also unresolved: the scenario floor
  is 15,000,000 while the sum of the compiled carbon pools at offset -1 is
  about 2,747,522.
- The legacy scenario output directories are empty, so no legacy result table
  is available for a like-for-like comparison.

The Phase 1 baseline result is in ``ws4/evidence/baseline/summary.json`` and
``notes/reference/gavin-baseline-findings.md``. It records the harvest and
growing-stock trajectory against both the literal parity target and the LTSY
first guess. The LTSY estimate is in ``ws4/evidence/ltsy/``.

What a ws4 scenario needs
-------------------------

A ws4 scenario must record:

- the active account and its floor or band;
- the period range and period width;
- the weight and shape;
- the schedule seed and initialization;
- the runtime and iteration budget; and
- the evidence path.

A scenario is not complete until its ws4 run writes its own account values and
target report. Do not describe a deferred scenario as a result.

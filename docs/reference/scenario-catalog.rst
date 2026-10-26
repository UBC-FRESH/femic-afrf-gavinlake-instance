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

The difference between scenarios is the active objective and its floor.

Catalog
-------

.. list-table::
   :header-rows: 1
   :widths: 18 47 35

   * - ID
     - Objective
     - Legacy target
   * - ``scenario_01``
     - Maximize timber harvest
     - ``product.yield.managed.total`` >= 500,000 m³
   * - ``scenario_02``
     - Maximize carbon stocks, HWP emission 0
     - ``feature.carbon.managed.total.stock.0`` >= 15,000,000
   * - ``scenario_03``
     - Maximize carbon stocks, HWP emission 50
     - ``feature.carbon.managed.total.stock.50`` >= 15,000,000
   * - ``scenario_04``
     - Maximize carbon stocks, HWP emission 100
     - ``feature.carbon.managed.total.stock.100`` >= 15,000,000
   * - ``scenario_05``
     - Maximize carbon stocks, half-life
     - ``feature.carbon.managed.total.stock.half`` >= 15,000,000
   * - ``scenario_06``
     - Maximize carbon sequestration, HWP emission 0
     - ``feature.carbon.managed.total.flux.0`` >= 15,000,000
   * - ``scenario_07``
     - Maximize carbon sequestration, HWP emission 50
     - ``feature.carbon.managed.total.flux.50`` >= 15,000,000
   * - ``scenario_08``
     - Maximize carbon sequestration, HWP emission 100
     - ``feature.carbon.managed.total.flux.100`` >= 15,000,000
   * - ``scenario_09``
     - Maximize carbon sequestration, half-life
     - ``feature.carbon.managed.total.flux.half`` >= 15,000,000

The N variant differs in one carbon-stock floor and in its output paths. Its
matrix is incomplete, so it is not a runnable second scenario set.

Translation status
------------------

- ``scenario_01`` is translated into ``ws4/targets_legacy_harvest.yaml``.
- ``scenario_02`` through ``scenario_09`` are preserved in the source archive
  and are deferred to Phase 1 and Phase 4.
- The legacy scenario output directories are empty, so no legacy result table
  is available for a like-for-like comparison.

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

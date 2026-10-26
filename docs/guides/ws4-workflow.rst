ws4 Workflow
============

Runtime lane
------------

The ws4 dataset is the runtime contract. The legacy Patchworks package is the
benchmark reference. Do not edit a compiled Parquet table by hand; change the
legacy CSV, the derived fragment table, or the translation configuration, and
rebuild.

Build and validate
------------------

.. code-block:: bash

   ws4 ingest \
     --matrix data/legacy_gavinlake/tracks/H \
     --fragments data/legacy_gavinlake/fragments.csv \
     --out ws4/runtime/legacy_matrix
   ws4 validate --dataset ws4/runtime/legacy_matrix

The dataset contains the 12 ws4 tables: fragments, blocks, tracks, strata,
treatments, curves, features, products, protoaccounts, accounts, groups, and
messages. The manifest records the source hashes.

Scenario catalog
----------------

``ws4/scenarios/legacy_catalog.yaml`` records all nine legacy scenarios and
their translation status. Only the timber-harvest scenario is translated into
a ws4 target file. The eight carbon scenarios are deferred because the
compiled matrix does not carry the runtime duplicate stock/flux accounts and
the target units are unresolved. See ``ws4/scenarios/README.md``.

Baseline
--------

``ws4/schedules/baseline_evenflow.csv`` is the Phase 1 sustained-yield
baseline. Build it with ``ws4/build_baseline_schedule.py``:

.. code-block:: bash

   python ws4/build_baseline_schedule.py \
     --dataset ws4/runtime/legacy_matrix \
     --out ws4/schedules/baseline_evenflow.csv \
     --estimate ws4/evidence/baseline/estimate.json

The rule is clearcut at the minimum operable age (80 years), re-entered every
80 years, with first entries assigned to ten-year periods by a greedy
volume-balancing heuristic. It does not enforce spatial or patch targets.

.. code-block:: bash

   ws4 simulate \
     --dataset ws4/runtime/legacy_matrix \
     --schedule ws4/schedules/baseline_evenflow.csv \
     --years 300 \
     --out ws4/runtime/baseline_evenflow \
     --topology ws4/topology.csv \
     --patch-accounts ws4/patch_accounts.yaml
   ws4 report \
     --run ws4/runtime/baseline_evenflow \
     --targets ws4/targets_legacy_harvest.yaml \
     --out ws4/runtime/baseline_evenflow_report

The baseline produces a mean of 188,677.89 m³ per ten-year period, a minimum of
177,070.07, and a maximum of 197,806.62 m³. The copied legacy 500,000 m³ template floor is not feasible on this matrix
under the only available treatment. It is a parity reference, not an
AFRF-calibrated target; see ``notes/reference/legacy-target-provenance.md``. Growing stock falls
from 1,418,962.31 m³ to 495,510.56 m³, so the legacy 1,277,067 m³ floor at
period 30 is also not met. The target report records 31 below, 26 above, and 4
met entries.

Smoke run
---------

``ws4/schedules/smoke_age80_pulse.csv`` is a structural check, not a policy
baseline. It assigns one ``CC`` treatment at offset 0 to every fragment aged 80
or more. It produces about 1.26 million m³ in the first decade and then no
sustained harvest. Use it to prove the dataset and the account machinery run,
not to compare scenarios.

Optimize
--------

The translated targets are in ``ws4/targets_legacy_harvest.yaml``. They encode:

- a 500,000 m³ harvest floor in each of 30 ten-year periods (copied MKRF
  template value; parity reference, not an AFRF-calibrated target);
- a 1,277,067 m³ growing-stock floor at period 30; and
- an even-flow band of -1 to 1 with weight 1000.

The legacy scenario scripts define patch accounts but do not set patch share
targets. ws4 reports the patch accounts through ``ws4/patch_accounts.yaml`` and
does not constrain them in the translated target file.

An optimization run is deferred to Phase 4. Phase 1 produced the baseline; the
optimization needs a reviewed starting point and a decision about which legacy
targets are feasible on this matrix.

Patch accounts
--------------

``ws4/patch_accounts.yaml`` maps the legacy pin:

- ``patch.grpblk`` on ``product.area.managed.total`` with 20 m topology and
  size classes 0-1, 1-5, 5-40, 40-50, and 50+ ha;
- ``patch.sepblk`` on ``feature.area.managed.seral.le10`` with 100 m topology
  and size classes 0-40, 40-50, and 50+ ha.

The smoke evidence shows 38 ``patch.grpblk`` patches at offset 0 over
3,330.51 ha, with 94.85 percent of the area in the 50+ ha class. That is
expected for a one-year harvest pulse and is a check that the account and
topology machinery is live, not a policy finding.

Runtime outputs
---------------

``ws4/runtime/`` is ignored by Git. The committed evidence is a small JSON
summary plus the source and schedule files needed to reproduce it. If a run
becomes part of the public evidence, add a short note to ``CHANGE_LOG.md`` and
store the summary under ``ws4/evidence/``.

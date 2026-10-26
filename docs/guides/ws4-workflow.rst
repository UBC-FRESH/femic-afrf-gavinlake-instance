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

Simulate
--------

.. code-block:: bash

   ws4 simulate \
     --dataset ws4/runtime/legacy_matrix \
     --schedule ws4/schedules/smoke_age80_pulse.csv \
     --years 300 \
     --out ws4/runtime/smoke_age80 \
     --topology ws4/topology.csv \
     --patch-accounts ws4/patch_accounts.yaml

The smoke schedule is a structural check. It assigns one ``CC`` treatment at
offset 0 to every fragment aged 80 or more. It is not a policy baseline and it
does not meet the legacy harvest or flow targets.

Report
------

.. code-block:: bash

   ws4 report \
     --run ws4/runtime/smoke_age80 \
     --targets ws4/targets_legacy_harvest.yaml \
     --out ws4/runtime/smoke_age80_report

The report is useful for checking that the target reader and the account names
line up. The smoke run will show large target violations by design.

Optimize
--------

The translated targets are in ``ws4/targets_legacy_harvest.yaml``. They encode:

- a 500,000 m³ harvest floor in each of 30 ten-year periods;
- a 1,277,067 m³ growing-stock floor at period 30; and
- an even-flow band of -1 to 1 with weight 1000.

The legacy scenario scripts define patch accounts but do not set patch share
targets. ws4 reports the patch accounts through ``ws4/patch_accounts.yaml`` and
does not constrain them in the translated target file.

An optimization run is deferred to Phase 1. It needs a reviewed baseline
schedule first, otherwise the comparison confounds schedule construction with
search behaviour.

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

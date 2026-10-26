Instance Contract
=================

Purpose
-------

This repository is a public ws4 model instance for the Gavin Lake block of the
UBC Alex Fraser Research Forest. It has three jobs:

1. preserve the legacy Patchworks matrix as a benchmark reference;
2. translate that matrix into a validated ws4 dataset; and
3. record the evidence that says what matches and what does not.

It is not the FEMIC core package, the ws4 runtime package, the private financial
overlay, or the future merged AFRF model.

Scope
-----

In scope:

- the legacy Gavin Lake H matrix, spatial inventory, topology, pin, and scenario
  scripts;
- a derived ws4 fragment table and a validated ws4 dataset;
- translated harvest, growing-stock, and flow targets;
- structural parity evidence and a reproducible smoke run; and
- documentation of the data publication boundary and the merge contract.

Out of scope until a later phase:

- the FEMIC canonical from-scratch rebuild of Gavin Lake;
- populated legacy scenario outputs, which the archive does not contain;
- private cost, revenue, contractor-rate, and cash-flow surfaces;
- the Knife Creek block; and
- the merged AFRF model.

Inputs
------

Table: Gavin Lake inputs.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Path
     - Role
   * - ``data/legacy_gavinlake/tracks/H/``
     - Legacy compiled matrix: blocks, curves, features, products,
       treatments, strata, accounts, groups.
   * - ``data/legacy_gavinlake/spatial/fragments.shp``
     - Legacy fragment geometry and attributes, EPSG:3005.
   * - ``data/legacy_gavinlake/spatial/topo_fragments.csv``
     - Legacy proximal topology, 20 m and 100 m edges.
   * - ``data/legacy_gavinlake/analysis/AFRF_H.pin``
     - Legacy control entrypoint: 30 ten-year periods, topology, patch
       accounts, carbon accounts.
   * - ``data/legacy_gavinlake/fragments.csv``
     - Derived ws4 fragment table. It is not source data.
   * - ``ws4/topology.csv``
     - Topology copied from the legacy package for ws4.
   * - ``ws4/patch_accounts.yaml``
     - ``patch.grpblk`` and ``patch.sepblk`` reporting accounts.
   * - ``ws4/targets_legacy_harvest.yaml``
     - Translated legacy harvest and flow targets.

Outputs
-------

Generated runtime artifacts stay under ``ws4/runtime/`` and are ignored by Git.
Committed evidence lives under ``ws4/evidence/``.

The dataset contract is the ws4 manifest plus Parquet tables. The simulator and
optimizer read that dataset, not the legacy CSV files directly.

Reproducibility
---------------

The full rebuild is:

.. code-block:: bash

   ws4 ingest \
     --matrix data/legacy_gavinlake/tracks/H \
     --fragments data/legacy_gavinlake/fragments.csv \
     --out ws4/runtime/legacy_matrix
   ws4 validate --dataset ws4/runtime/legacy_matrix

The smoke simulation adds the topology and patch accounts:

.. code-block:: bash

   ws4 simulate \
     --dataset ws4/runtime/legacy_matrix \
     --schedule ws4/schedules/smoke_age80_pulse.csv \
     --years 300 \
     --out ws4/runtime/smoke_age80 \
     --topology ws4/topology.csv \
     --patch-accounts ws4/patch_accounts.yaml

See :doc:`ws4-workflow` for the runbook and :doc:`legacy-intake` for the
provenance and parity check.

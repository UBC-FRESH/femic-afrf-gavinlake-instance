Legacy Intake
=============

Source archive
--------------

The legacy package was supplied by the maintainer as ``AFRF.zip`` on
2026-10-26. It is a compiled Patchworks model package built by Cosmin Man. The
archive SHA-256 is:

.. code-block:: text

   3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19

The full entry list and the disposition of every entry are recorded in
``metadata/legacy_archive_inventory.csv``. The hash is repeated in
``metadata/legacy_archive.sha256``.

What the archive contains
-------------------------

The package has two compiled variants:

- ``AFRF/tracks/H/`` is complete: blocks, curves, features, products,
  treatments, strata, track names, accounts, protoaccounts, groups, messages,
  packages, and sequences.
- ``AFRF/tracks/N/`` is incomplete: it has blocks, curves, features, groups,
  messages, and packages, but no products, treatments, strata, or track names.
  It is not a runnable replacement for H.

The H variant is the benchmark source for this instance. It contains:

======================  ==============================================
Surface                 Count
======================  ==============================================
Blocks                  2,907
Managed area            5,663.66 ha
Tracks                  97
Curve points            48,288
Feature rows            3,201
Product rows            5,141
Treatment rows          97
Account rows            115
======================  ==============================================

The spatial inventory has 2,907 fragments in EPSG:3005. The
``CONTCLAS`` split is 1,505 ``C`` fragments (4,663.01 ha) and 1,402 ``N``
fragments (1,000.66 ha). All blocks join one-to-one on ``RES_KEY`` to
``BLOCK``.

The archive does **not** contain:

- a ForestModelXML recipe;
- populated scenario output directories (the scenario trees are empty);
- yield files (the ``yields`` directories are empty); or
- the original Excel workbooks.

Sanitization
------------

The public copy was normalized to LF line endings and the home-directory
comments were replaced with ``[legacy-path]``. The numeric values in the CSVs
and the decisions in the pin are unchanged. Machine-specific build and log
files that are not needed for the ws4 benchmark were left out of the public
copy and are listed with a disposition in the inventory.

Derived fragment table
----------------------

``data/legacy_gavinlake/fragments.csv`` is derived, not source data. It joins
the legacy ``blocks.csv`` to ``fragments.shp`` on ``RES_KEY = BLOCK`` and adds:

- ``BLOCK`` and ``TRACK`` from the legacy matrix;
- ``AREA_HA`` from ``Shape_Area / 10000``;
- ``F_AGE`` from ``AGE_2019``; and
- ``AGE_RAW`` and ``AGE_CLIPPED`` for audit.

Why clip age
------------

The legacy package uses ``AGE_2019 = -2`` as a non-forest sentinel. There are
87 such fragments. ws4 requires non-negative age, so ``F_AGE`` clips them to
zero and keeps the raw value. The initial growing-stock parity check below
shows that the convention does not disturb the productive-forest aggregate.

A second derived file, ``fragments_managed.csv``, keeps only ``CONTCLAS = C``
fragments with a non-negative raw age. It is available for sensitivity runs; it
is not the primary dataset.

Structural parity
-----------------

The legacy scenario script constrains ``feature.yield.managed.total`` to at
least 1,277,067 m³ at period 30 and describes that as 90 percent of initial
growing stock. The implied initial value is therefore 1,418,963.33 m³.

The ingested ws4 dataset reports an initial value of 1,418,962.31 m³. The
relative difference is -7.2 × 10⁻⁷. This is the first acceptance gate for the
benchmark: it says that the block area, track assignment, age, and yield-curve
aggregation survive the translation.

The evidence is written to ``ws4/evidence/legacy_ingest.json``. The smoke
simulation evidence is in ``ws4/evidence/smoke_age80/summary.json``.

Known gaps
----------

- The archive has no ForestModelXML, so the ws4 path is an ingestion of the
  compiled matrix, not a recipe rebuild. The canonical FEMIC rebuild remains a
  later lane.
- The archive has no populated scenario outputs, so there is no legacy result
  table to compare against. The benchmark compares structure, initial
  conditions, and translated policy, not a historical solver run.
- The N variant is incomplete. Do not use it as a second scenario without
  reconstructing its missing tables.

Legacy-to-ws4 Crosswalk
=======================

This page records how the legacy Patchworks surfaces map to ws4. It is a
companion to ``ws4/README.md`` and the source pin at
``data/legacy_gavinlake/analysis/AFRF_H.pin``.

Matrix tables
-------------

============================  ==========================  ==================================
Legacy file                   ws4 table                   Mapping
============================  ==========================  ==================================
``blocks.csv``                ``blocks``                  ``BLOCK`` to ``block_id``,
                                                          ``TRACK`` to ``track_id``,
                                                          ``OFFSET`` to ``offset``,
                                                          ``AREA`` to ``area_ha``.
``tracknames.csv``            ``tracks``                  ``TRACK`` to ``track_id``,
                                                          ``STRATA`` to ``name``.
``strata.csv``                ``strata``                  ``TRACK``, ``OFFSET``,
                                                          ``NEXTAGE`` to ``next_age``,
                                                          ``CYCLE`` to ``cycle``.
``treatments.csv``            ``treatments``              ``TRACK`` to ``track_id``,
                                                          ``BEGIN``/``END``,
                                                          ``TREATMENT``,
                                                          ``NEWTRACK`` to
                                                          ``new_track``, ``OFFSET``,
                                                          ``RETAIN``.
``curves.csv``                ``curves``                  ``CURVE`` to ``curve_id``,
                                                          ``X``/``Y`` to ``x``/``y``.
``features.csv``              ``features``                ``TRACK``, ``LABEL``,
                                                          ``CURVE`` to ``curve_id``.
``products.csv``              ``products``                ``TRACK``, ``TREATMENT``,
                                                          ``LABEL``, ``CURVE`` to
                                                          ``curve_id``.
``accounts.csv``              ``accounts``                ``GROUP``, ``ATTRIBUTE``,
                                                          ``ACCOUNT``, ``SUM``.
``protoaccounts.csv``         ``protoaccounts``           Same columns as accounts.
``groups.csv``                ``groups``                  ``BLOCK`` to ``block_id``,
                                                          ``GROUP``.
``messages.csv``              ``messages``                Empty legacy table; no
                                                          message rows.
============================  ==========================  ==================================

Spatial and topology
--------------------

============================  ==================================================
Legacy surface                ws4 use
============================  ==================================================
``fragments.shp``             Source geometry and attributes. The derived
                              ``fragments.csv`` carries ``BLOCK``, ``TRACK``,
                              ``AREA_HA``, and ``F_AGE``.
``topo_fragments.csv``        Copied to ``ws4/topology.csv``. The header is
                              already ``BLOCK1,BLOCK2,DISTANCE,LENGTH``.
``RES_KEY``                   Stable block key. It joins one-to-one to
                              ``BLOCK``.
``CONTCLAS``                  ``C`` is productive forest, ``N`` is non-forest.
                              See the age-clipping note.
``AGE_2019``                  Source age. ``-2`` is a non-forest sentinel and is
                              clipped to ``F_AGE = 0``.
============================  ==================================================

Control surfaces
----------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Legacy surface
     - ws4 use
   * - ``Horizon.setHorizon(30, 10)``
     - 30 ten-year periods, 300 years. Targets use ``period_width: 10``.
   * - ``control.inputTopology(..., 20d)``
     - ``patch.grpblk`` with ``search_distance: 20.0``.
   * - ``control.inputTopology(..., 100d)``
     - ``patch.sepblk`` with ``search_distance: 100.0``.
   * - ``control.addPatchTarget(...)``
     - Patch accounts are reporting surfaces. The legacy scenarios do not set
       patch share targets.
   * - ``RATIO_ACCOUNTS.bsh``
     - ``product.flow.yield.even`` becomes a ws4 ``flow: even`` target on
       ``product.yield.managed.total``.
   * - ``scenarios_AFRF_H.bsh``
     - Harvest, growing-stock, flow, and carbon scenario definitions. See
       :doc:`scenario-catalog`.
   * - ``00_Build_Matrix.bsh``
     - Not used: it points at an MKRF path and needs the missing
       ForestModelXML.
   * - ``02_export_toCBM.bsh``
     - Not used: it is a CBM export surface, not a ws4 runtime input.

Known translation limits
------------------------

- The archive has no ForestModelXML, so ws4 ingests the compiled matrix rather
  than compiling a recipe.
- The legacy carbon accounts are preserved as account definitions and curves.
  Their scenario targets are not yet translated into ws4 target files.
- The legacy patch accounts are preserved for reporting. No patch share target
  is active in the translated scenario set.
- The non-forest sentinel is clipped for ws4 age validity. The raw value and a
  clipped flag are kept in the derived fragment table.

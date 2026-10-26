# Gavin Lake context

This note records the public context for the block. It is not a substitute for
the legacy matrix or the spatial inventory.

## Location and area

- Gavin Lake is the northern block of the UBC Alex Fraser Research Forest, near
  Beaver Valley and Quesnel Lake, north-east of 150 Mile House, British
  Columbia.
- The AFRF Management and Working Plan #2 describes the block as 6,315 ha.
- A public location reference is UTM zone 10U, NAD83, approximately
  581272 E, 5816186 N.
- The legacy matrix net area is 5,663.66 ha. That is the compiled model area,
  not necessarily the gross legal area.

## Biogeoclimatic setting

- The block is primarily SBSdw1, with a significant ICHmk3 component.
- The SBSdw1 is dominated by mixed Douglas-fir, lodgepole pine, and trembling
  aspen.
- The ICHmk3 supports western redcedar, hybrid spruce, and subalpine fir.
- The legacy `fragments.shp` BEC values are `SBSdw1`, `ICHmk3`, and
  `ICHmk3/SBSdw`.

## Legacy model

- The package is a compiled Patchworks matrix, not a source recipe.
- The H variant is complete and is the benchmark source.
- The N variant is incomplete and is not runnable.
- The model has 30 ten-year periods (300 years), a 20 m topology for
  `patch.grpblk`, and a 100 m topology for `patch.sepblk`.
- The legacy scenario scripts define nine scenarios: one timber-harvest
  scenario and eight carbon stock/sequestration scenarios.

## Sources

- AFRF Management and Working Plan #2, public PDF on the AFRF site.
- AFRF block-location page, public.
- The legacy archive and its inventory under `data/legacy_gavinlake/`.

## Uncertainty

- The public context is not a substitute for the legal boundary or the current
  inventory.
- The legacy matrix has no populated scenario outputs, so it is a structural
  benchmark, not a historical solver replay.

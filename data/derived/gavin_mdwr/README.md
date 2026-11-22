# Gavin MDWR derived spatial layers

Retrieved 2026-11-22 from the BC Geographic Warehouse. Both layers are clipped
to the Gavin Lake block fragments in this instance.

## `uwr_approved_clip.geojson`

- Source layer:
  `WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP`
- WFS:
  `https://openmaps.gov.bc.ca/geo/pub/WHSE_WILDLIFE_MANAGEMENT.WCP_UNGULATE_WINTER_RANGE_SP/ows`
- Bounding box used for retrieval:
  `52.15,-122.35,52.75,-121.15` (WGS 84)
- Result: **U-5-002 / dwl_9 (Beaver Valley North)**, **2,726.42 ha**
- CRS: EPSG:3005
- `area_ha` is the clipped area, computed in EPSG:3005.

The 2004 U-5-002 order PDF is a one-page order. Schedule A is the approved
spatial layer, not a map embedded in that PDF.

## `stand_structure_habitat_class_clip.geojson`

- Source layer:
  `REG_LAND_AND_NATURAL_RESOURCE.WLD_MULE_DEER_STND_STRC_CAR_SP`
- WFS:
  `https://openmaps.gov.bc.ca/geo/pub/REG_LAND_AND_NATURAL_RESOURCE.WLD_MULE_DEER_STND_STRC_CAR_SP/ows`
- Clipped to the UWR clip above.
- CRS: EPSG:3005
- Class areas:
  - High: **697.92 ha**
  - Moderate: **1,013.18 ha**
  - Low: **1,015.33 ha**

These are the stand-structure habitat class polygons referenced by GWM 7. They
are not the adjusted Appendix 9 compartment boundaries.

## Caveat

The current group estate is 2,797.5 ha; the authoritative UWR clip is
2,726.42 ha. The approximately 71 ha difference must be reconciled before a
compliance claim.

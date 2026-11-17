# Gavin Lake full-estate 3D scene

`gavin_scene.json` is the WS4 studio-3D scene pack for the Gavin Lake instance.

- 2,907 legacy block polygons
- 2024 LidarBC 5 m DEM/CHM terrain and canopy
- approximately 3.96M synthetic stem positions at 700 TPH
- no Gavin species inventory is present; stems are displayed as conifer
- CHM coverage is about 75% of the block area. CHM no-data gaps are filled from block height for display only, and are labelled as fallback, not measured canopy. Terrain no-data gaps use SRTM.
- the scene starts on a central production block and opens at a stand-scale camera so trunks are visible; wheel out for the full estate view
- source: LidarBC 2024 DSM/DEM pairs, public legacy block polygons

The scene is a visual screening product, not a measured tree inventory.

Build command:

```bash
python scripts/build_afrf_studio3d.py \
  --blocks data/legacy_gavinlake/spatial/fragments.shp \
  --id-field RES_KEY \
  --default-density 700 \
  --default-height 25 \
  --dem data/lidar/gavin_2024/dem_5m.tif \
  --chm data/lidar/gavin_2024/chm_5m.tif \
  --srtm-dir /path/to/srtm \
  --label "Gavin Lake · full-estate 3D scene" \
  --source-note "LidarBC 2024 5 m DEM/CHM; synthetic stems; no species inventory." \
  --out planning/studio3d/gavin_scene.json
```

# Gavin Lake full-estate 3D scene

`gavin_scene.json` is the WS4 studio-3D scene pack for the Gavin Lake instance.

- 2,907 block polygons
- SRTM 1 arc-second terrain
- synthetic stems at 700 TPH (about 3.96M nominal stems)
- no Gavin CHM; canopy is labelled synthetic
- source: public legacy block polygons and SRTM terrain

The scene is a visual screening product, not a measured tree inventory.

Build command:

```bash
python scripts/build_afrf_studio3d.py \
  --blocks data/legacy_gavinlake/spatial/fragments.shp \
  --id-field RES_KEY \
  --default-density 700 \
  --default-height 25 \
  --srtm-dir /path/to/srtm \
  --label "Gavin Lake · full-estate 3D scene" \
  --out planning/studio3d/gavin_scene.json
```

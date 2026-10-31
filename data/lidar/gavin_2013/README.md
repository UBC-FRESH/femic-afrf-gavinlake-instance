# Gavin Lake 2013 canopy tree inventory (partial)

`runbooks/detect_gavin_2013_trees.py` applies the Knife Creek 2013 LAS
calibration (window 3, minimum height 3 m, NMS radius 1.5 m) to the 11 2013 LAS
tiles that overlap southern Gavin Lake.

Result:

- 11 tiles, 339 ha of the 5,664 ha block.
- 166,188 canopy trees.
- Mean height 21.1 m; mean DBH estimate 28.5 cm; 490 TPH.
- Species unknown; DBH is height allometry.
- `trees.csv` and `trees.gpkg` are the full detection output and are not
  committed because they are large.
- `block_piece_size.csv` is the 111-fragment summary.
- `fhops/gl_0323/` is a validated FHOPS tree-inventory pilot for fragment 323.

This is a partial canopy inventory, not a CFI. The southern Gavin coverage is
the only standard-LAS Gavin coverage in the OneDrive payload; there are no 2019
or 2024 Gavin tiles.

## Superseded for full-block coverage

The 2009 FUSION LIDARBIN covers the full Gavin block and has been processed at
`data/lidar/gavin_2009/`. This 2013 partial inventory remains as an independent
sensor/vintage check for the southern overlap.

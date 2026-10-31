# Gavin Lake 2009 canopy tree inventory

The 2009 `.las` files are valid FUSION `LIDARBIN`, not corrupted LAS. They were
processed with FUSION/LDV 4.61 under Wine:

- `Catalog` for tile extents;
- `GridSurfaceCreate /minimum` for the bare-earth surface from the `gd` tiles;
- `canopymodel /ground:` for the normalized canopy surface from the `pt` tiles;
- `CanopyMaxima /threshold:3` for the tree list.

The run processed 100 `pt` tiles and retained 1,116,962 trees in 2,793
fragments. Heights were filtered to 2-60 m to remove bare-earth and tile-edge
artifacts.

Summary:

- Area: 5,663.7 ha.
- Trees: 1,116,962.
- TPH: 197.2.
- Mean height: 15.0 m; p95 32.7 m; max 59.8 m.
- Mean DBH estimate: 19.8 cm; p50 15.0 cm; max 88.7 cm.
- 2,793 of 2,907 fragments have at least one detected canopy tree.

`trees.csv` and `trees.gpkg` are the full point outputs and remain uncommitted
because they are large. `trees_filtered.csv` and `trees_filtered.gpkg` are the
filtered versions. `block_piece_size.csv` is the fragment summary.
`fhops/gl_0323/` is a validated FHOPS tree-inventory pilot.

This is a 2009 canopy inventory, not a CFI. Species are unknown and DBH is
height allometry.

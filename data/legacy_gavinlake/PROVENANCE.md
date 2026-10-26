# Legacy Gavin Lake package provenance

## Source

The legacy AFRF Gavin Lake Patchworks model package was supplied by the
maintainer on 2026-10-26 as `AFRF.zip`. It was built by Cosmin Man about a
decade earlier and recompiled in 2025.

Archive SHA-256:

```text
3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19
```

The archive itself is not committed. The public copy is the sanitized package
under this directory, and `../../metadata/legacy_archive_inventory.csv` records
every archive entry and its disposition.

## Contents

The package has two compiled variants:

- `tracks/H/` is complete and is the benchmark source.
- `tracks/N/` is incomplete: it has no products, treatments, strata, or track
  names. It is not a runnable replacement for H.

The H matrix contains 2,907 blocks over 5,663.66 ha, 97 tracks, 48,288 curve
points, 3,201 feature rows, 5,141 product rows, and 115 account rows. The
spatial inventory is in EPSG:3005. The proximal topology is
`spatial/topo_fragments.csv`.

## Derived files

- `fragments.csv` — the ws4 fragment table. It joins `blocks.csv` to
  `fragments.shp` on `RES_KEY = BLOCK`, takes area from `Shape_Area / 10000`,
  takes age from `AGE_2019`, and keeps `AGE_RAW` and `AGE_CLIPPED` for audit.
- `fragments_managed.csv` — the `CONTCLAS = C` and non-negative-age subset, for
  sensitivity runs. It is not the primary dataset.
- `../../ws4/topology.csv` — a copy of `spatial/topo_fragments.csv` for ws4.

The age clipping is a translation, not a source correction. The legacy package
uses `AGE_2019 = -2` as a non-forest sentinel for 87 fragments. ws4 requires a
non-negative age.

## Sanitization

The public copy normalizes text files to LF and replaces home-directory
comments with `[legacy-path]`. The numeric values and the model logic are
unchanged. Machine-specific build and log files that are not needed for the
ws4 benchmark are omitted; their archive entries and dispositions are in the
inventory.

## What is missing

- No ForestModelXML recipe.
- No populated scenario output directories; they are empty trees.
- No yield files in `yields/`.
- No original Excel workbooks.

The ws4 path is therefore an ingestion of the compiled matrix, not a recipe
rebuild. See `../docs/guides/legacy-intake.rst` and
`../notes/adr/0002-ws4-runtime-lane.md`.

## Terms

The legacy model data and the AFRF spatial inventory retain their source terms.
The repository's MIT license covers the original code and documentation, not a
relicensing of this data.

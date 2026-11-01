# UBC 2009 LiDAR: format diagnosis and fix

Date: 2026-10-31
Status: fixed; full Gavin processing in progress

## Finding

The 2009 files are **not corrupted**. They are valid FUSION/LDA `LIDARBIN`
files with a `.las` extension.

- First eight bytes: `LIDARBIN`.
- Header version: 1.0.
- The paired `.lasd` files are valid OLE compound documents containing the
  FUSION `BasicDatasetInfo`, `BasicHeaderInfo`, `DatasetStatistics`, and
  `FileStatistics` streams.
- DataLad `git annex fsck` reports the annex copy OK.
- The 2013 files start with `LASF`; the 2009 files start with `LIDARBIN`.

The extension is the only thing that looks like LAS. The bytes are the older
FUSION binary point format. Our audit used `laspy`, which correctly refused a
non-`LASF` file. Calling the data “unreadable” was our reader limitation, not a
data defect.

## Where the data was “fucked”

It was not corrupted in transit. The DataLad annex objects pass `fsck`, and the
file signatures match the producer’s FUSION format. The failure was in our
ingest assumption: `laspy` expects standard LAS/LAZ, and the 2009 payload is
FUSION LIDARBIN. The `.las` suffix comes from the delivered payload; the header
is authoritative.

## Fix

Use the public-domain FUSION/LDV 4.61 command-line tools under Wine:

- `Catalog.exe` reads the LIDARBIN tile extents.
- `GridSurfaceCreate.exe /minimum` builds the bare-earth surface from the `gd`
  tiles.
- `canopymodel.exe /ground:` builds a normalized canopy surface from the `pt`
  tiles.
- `CanopyMaxima.exe /threshold:3` detects canopy trees.

The 32-bit tools are required because the available `mfc140.dll`/`msvcp140.dll`
runtime is 32-bit. The 64-bit binaries fail with `c000007b` when paired with the
32-bit runtime.

Test tile `pt000001` / `gd000001` produced a valid normalized CHM and 5,191
canopy maxima. The full 2009 Gavin run is processing the 100 `pt` tiles that
intersect the block.

## What the 2009 data covers

The 2009 tile grid covers Gavin Lake, not Knife Creek:

- `gd` tiles: ground-return subset.
- `pt` tiles: full point cloud.
- 100 `pt` tiles intersect the Gavin fragment bounds.
- The 2009 extents are about 580-592 km E and 5,809-5,817 km N (UTM 10N), which
  is the Gavin block.

Knife Creek is covered by 2013 LAS, 2019 rasters, and 2024 LidarBC tiles.

## What to tell Ionut

The data is good. The 2009 files are valid FUSION LIDARBIN with a `.las`
extension, and DataLad checksums pass. Our reader assumed standard LAS, so we
misclassified the format. We installed FUSION/LDV and are converting/processing
the 2009 tiles directly. No reupload is needed.

If he wants to help, ask for:

- the projection/units metadata for the 2009 acquisition;
- confirmation that `gd` is the ground-return subset and `pt` is the full point
  cloud;
- the return-number and classification conventions; and
- the vendor/acquisition report, if available.

## Commands

```bash
# Test one tile
wine /path/to/FUSION/LDA2LAS.exe gd000001.las gd000001_std.las
wine /path/to/FUSION/GridSurfaceCreate.exe /minimum ground.dtm 1 M M 1 10 2 0 gd000001.las
wine /path/to/FUSION/canopymodel.exe /ground:ground.dtm chm.dtm 1 M M 1 10 2 0 pt000001.las
wine /path/to/FUSION/CanopyMaxima.exe /threshold:3 /summary chm.dtm trees.csv

# Full Gavin runbook
python runbooks/build_gavin_2009_trees.py \
  --las-dir external/.../LiDAR/2009 \
  --fusion-dir /path/to/FUSION \
  --wineprefix /path/to/wineprefix \
  --out-dir data/lidar/gavin_2009
```

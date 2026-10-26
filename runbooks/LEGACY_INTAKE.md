# Legacy intake runbook

Status: reproducible procedure. The source archive is not committed.

## 1. Verify the archive

```bash
sha256sum AFRF.zip
```

The expected digest is:

```text
3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19
```

If it differs, stop. Do not overwrite `metadata/legacy_archive.sha256`.

## 2. Inventory the archive

```bash
python - <<'PY'
import csv, zipfile
from pathlib import Path
with zipfile.ZipFile('AFRF.zip') as z:
    for info in z.infolist():
        print(info.filename, info.file_size, info.compress_size)
PY
```

Compare the result with `metadata/legacy_archive_inventory.csv`. The inventory
records the disposition of every entry, including omitted machine-specific
files.

## 3. Prepare the fragment table

The committed `data/legacy_gavinlake/fragments.csv` is derived from:

- `data/legacy_gavinlake/tracks/H/blocks.csv`;
- `data/legacy_gavinlake/spatial/fragments.shp`.

The join is `RES_KEY = BLOCK`. Area is `Shape_Area / 10000`. Age is
`AGE_2019`, clipped at zero for ws4, with `AGE_RAW` and `AGE_CLIPPED` kept for
audit.

If the source changes, regenerate the file and record the new hash. Do not edit
the CSV by hand.

## 4. Sanitize the text copy

The public copy uses LF line endings and replaces home-directory comments with
`[legacy-path]`. The numeric values are unchanged. Record the normalization in
the provenance note if the source is refreshed.

## 5. Ingest and validate

```bash
ws4 ingest \
  --matrix data/legacy_gavinlake/tracks/H \
  --fragments data/legacy_gavinlake/fragments.csv \
  --out ws4/runtime/legacy_matrix
ws4 validate --dataset ws4/runtime/legacy_matrix
```

## 6. Record the parity evidence

Run the parity check and write `ws4/evidence/legacy_ingest.json`. The key value
is the initial `feature.yield.managed.total` at offset -1. It should be close
to 1,418,963 m³, the value implied by the legacy 1,277,067 m³ floor at 90
percent of initial growing stock.

## 7. Smoke simulation

```bash
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/smoke_age80_pulse.csv \
  --years 300 \
  --out ws4/runtime/smoke_age80 \
  --topology ws4/topology.csv \
  --patch-accounts ws4/patch_accounts.yaml
```

The smoke schedule is a structural check, not a policy baseline. Record the
summary under `ws4/evidence/smoke_age80/summary.json`.

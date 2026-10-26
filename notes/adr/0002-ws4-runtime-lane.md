# ADR 0002: ws4 is the Gavin Lake runtime lane

Status: accepted
Date: 2026-10-26

## Context

The legacy AFRF Gavin Lake package is a compiled Patchworks matrix. It contains
`tracks/H/`, `spatial/fragments.shp`, `spatial/topo_fragments.csv`, the pin,
and the scenario scripts. It does **not** contain a ForestModelXML recipe or
the original workbooks.

The instance needs a runnable model now, and a benchmark that preserves the
legacy structure. A canonical FEMIC from-scratch rebuild is a separate lane
that needs source data the archive does not carry.

## Decision

Use the compiled legacy matrix as the input to the **ws4 ingest** path:

```bash
ws4 ingest \
  --matrix data/legacy_gavinlake/tracks/H \
  --fragments data/legacy_gavinlake/fragments.csv \
  --out ws4/runtime/legacy_matrix
```

The legacy Patchworks package is the reference and benchmark lane. The ws4
compiled dataset is the runtime lane.

The derived fragment table is committed because it is small and it makes the
ingest reproducible. Its construction is documented in
`docs/guides/legacy-intake.rst`.

## Alternatives considered

- **Rebuild from a ForestModelXML recipe.** Not possible from this archive: no
  XML was supplied.
- **Run Patchworks directly.** The package is proprietary and the runtime is
  not the target lane.
- **Reconstruct the XML from the tracks.** Possible in principle, but it would
  invent the recipe inputs and weaken the benchmark.

## Consequences

- The benchmark is a structural and initial-condition comparison, not a
  historical solver replay. The archive has no populated scenario outputs.
- The canonical FEMIC rebuild remains a later lane, and it needs source data
  outside this archive.
- The fragment table is derived and must be regenerated if the source archive
  changes.
- The ws4 dataset keeps the legacy block, track, curve, treatment, and account
  names. The merge contract in ADR 0003 preserves them.

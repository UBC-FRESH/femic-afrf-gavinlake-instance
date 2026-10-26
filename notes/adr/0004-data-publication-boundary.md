# ADR 0004: Data publication boundary

Status: accepted
Date: 2026-10-26

## Context

This is a public model instance. The legacy package contains a compiled model,
a spatial inventory, and scenario scripts. It does not contain the private
cost/revenue workbooks that the MKRF instance keeps out of its public surface.

A public repository still needs an explicit boundary. A file can be readable
and still not be cleared for publication.

## Decision

Publish the open model and evidence:

- the sanitized legacy H matrix, spatial inventory, topology, pin, and
  scenario scripts;
- the derived fragment tables;
- the ws4 translation files, schedules, and evidence;
- documentation, ADRs, and provenance ledgers.

Do not publish:

- raw cost, revenue, contractor-rate, and cash-flow workbooks;
- private financial overlays;
- credentials, tokens, and keys;
- machine-specific paths and personal identifiers; and
- unpublished third-party documents.

Sanitize text files to LF and replace home-directory comments with
`[legacy-path]`. Leave machine-specific build and log files out of the public
copy; record their disposition in the archive inventory.

## Consequences

- The legacy data values are unchanged, but the text formatting and
  home-directory comments are normalized.
- The archive hash and the full entry inventory are the provenance record.
- The MIT license covers the original code and documentation, not a
  relicensing of the legacy data.
- A future restricted source needs its own decision and provenance note.

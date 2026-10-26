# ADR 0001: Two block instances, one future merged model

Status: accepted
Date: 2026-10-26

## Context

The UBC Alex Fraser Research Forest has two geographically disconnected blocks:
Gavin Lake and Knife Creek. They differ in ecology, management objective, and
growth engine. Gavin Lake has a legacy Patchworks matrix and a largely
age-class, even-aged history. Knife Creek is predominantly IDF, has
mule-deer winter-range constraints over almost the whole block, and requires
uneven-aged continuous cover selection.

A single model built now would force one growth engine and one policy surface
onto both blocks. It would also make the Gavin Lake legacy benchmark harder to
interpret.

## Decision

Build and maintain two independent ws4 model instances:

- `UBC-FRESH/femic-afrf-gavinlake-instance`
- `UBC-FRESH/femic-afrf-knifecreek-instance`

Each instance owns its source data, growth engine, policy, evidence, and
release cadence. Each compiles to the same ws4 compiled-dataset schema.

Reserve `UBC-FRESH/femic-afrf-instance` for a future merged model. The merged
model is a composition problem, not a reason to couple the two block repos now.

## Consequences

- The Gavin Lake legacy benchmark can use its native matrix and parity checks
  without a Knife Creek state-transition library.
- Knife Creek can use FVS-BC and a state-transition library without forcing
  Gavin Lake onto FVS-BC.
- The merge is a later, explicit project with its own identifier, topology,
  target, and provenance contracts.
- The two instances must keep their schemas compatible: same ws4 table
  contracts, same account vocabulary where the concept is shared, and
  namespaced identifiers where they are not.

## Reserved identifiers

- Gavin Lake block IDs stay native (`1..999,999`).
- Knife Creek block IDs are offset by `1,000,000` in the merged model.
- Track, curve, and fragment IDs are namespaced in the merged model; the
  block-level instances keep their native IDs.
- The merged model is `femic-afrf-instance`.

The detailed merge contract is ADR 0003.

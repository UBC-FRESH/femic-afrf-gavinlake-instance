# ADR 0003: Merged AFRF model contract

Status: proposed
Date: 2026-10-26

## Context

The Gavin Lake and Knife Creek instances are separate ws4 models. A future
merged model is useful for global accounting and for optimized scenarios that
trade harvest and habitat between the two blocks. The blocks are geographically
disconnected: there is no cross-block adjacency, road network, or shared stand.

The two instances do not share a growth engine. Gavin Lake uses a legacy
Patchworks age-class matrix. Knife Creek uses an FVS-BC state-transition
library. They do share the ws4 compiled-dataset schema.

## Decision

Create a third repository, `UBC-FRESH/femic-afrf-instance`, when the merge is
funded and scoped. It composes the two block instances; it does not copy their
source data or reimplement their growth engines.

The merged model is a true ws4 dataset, not only a post-hoc sum of two runs:

- both block datasets are compiled to ws4 tables;
- the tables are concatenated with namespaced identifiers;
- the topology is block-diagonal;
- the target set can be global, block-specific, or both; and
- the run reports keep block-level attribution.

## Identifier contract

- Block IDs: Gavin Lake keeps its native `RES_KEY`/`BLOCK` values
  (`1..999,999`). Knife Creek block IDs are offset by `1,000,000`.
- Fragment IDs: allocate from a merged sequence and keep a crosswalk to the
  source fragment ID.
- Track IDs: Gavin Lake keeps `1..99,999`. Knife Creek is offset by `100,000`
  or a larger reserved range.
- Curve IDs: offset Knife Creek by a reserved range; keep a crosswalk.
- Treatment names: use the same name for the same concept. Gavin Lake `CC` and
  Knife Creek `SEL_*` are different concepts and keep different names.
- Account names: use the global vocabulary for shared concepts
  (`product.yield.managed.total`, `feature.yield.managed.total`, carbon
  accounts). Use a suffix only where the semantics differ.
- Group names: prefix with `gl.` or `kc.` for block-specific groups.

## Topology contract

- The merged topology is the union of the block topologies.
- No edge may cross blocks. A merge validation fails on a cross-block edge.
- Patch accounts are defined on the merged topology; a patch cannot span
  blocks.
- Spatial constraints that are block-specific stay block-specific.

## Merge options

1. **Composite reporting.** Run each instance independently and sum the account
   values. Cheap; cannot optimize a global objective.
2. **True merged dataset.** Concatenate tables with namespaced IDs and optimize
   the union. Required for global accounting in optimized scenarios.

The merged repository should support both, with (2) as the primary path.

## Open questions

1. How are the different track semantics documented in one dataset without a
   free-text provenance column? A merge manifest is the current answer.
2. How are global harvest targets allocated to blocks when the growth engines
   have different productivity and constraints?
3. Which mule-deer and other block-specific constraints become global
   constraints, and which stay local?
4. How are the two growth engines' carbon accounts reconciled?
5. What is the release cadence of the merged model relative to the block
   instances?
6. Does the merged model need its own data package, or only the compiled
   datasets?

## Consequences

- The block instances must keep their native identifiers stable.
- The block instances must keep the ws4 schema compatible.
- The merge is a separate project with its own roadmap, tests, and release.
- A merged result must be attributable to its source block; a global number
  without block attribution is not enough.

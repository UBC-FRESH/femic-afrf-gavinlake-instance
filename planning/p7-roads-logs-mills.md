# P7 - Roads, log sorts, and mills

Date: 2026-10-31
Status: planned
Parent issue: TBD
Branch: `feature/p7-roads-logs-mills`

## Goal

Add a delivered-wood layer to the Gavin Lake model: road access, route cost,
mills, log sorts, and harvest-system constraints. The layer is built on the
existing legacy-matrix baseline and does not replace the growth, volume, or
carbon work.

The phase adds:

- a road network and block-to-road linkage;
- build, maintenance, and haul accounts;
- a mill register and product eligibility;
- log-grade and log-sort products with an interior price basis; and
- harvest-system classes and access constraints.

It does not set AAC, tune even-flow, or claim legal access or legal compliance.

## Current state

The Gavin Lake instance has:

- 2,907 blocks over 5,663.66 ha;
- a 300-year, 30-period baseline with clearcut at age 80 and re-entry every
  80 years;
- a compiled ws4 dataset and baseline run; and
- no road layer, no route configuration, no mill register, and no log-price
  basis.

The 2007 AFRF Management and Working Plan #3 gives the planning context:

- Gavin Lake net area: 4,922 ha;
- existing roads: 112.2 km, 168.3 ha right-of-way, 2.28 km/km2, 3.4% of area;
- planned roads: 136.1 km, 204.1 ha, 2.77 km/km2, 4.1% of area;
- planned increase: 23.9 km and 35.8 ha;
- maximum sustained favourable grade: 12%;
- maximum sustained adverse grade: 8%;
- maximum skid distance: 400 m;
- no circular routes;
- areas above 30% slope are candidates for cable systems, and areas above 60%
  are generally inaccessible; and
- the annual road-construction program is 0.5-3 km, with planned roads intended
  within 15 years.

The plan's Appendix 11 Gavin Lake access map shows primary, secondary,
unimproved, landing, proposed-road, bridge, gate, culvert, and other road
features. It has a scale bar and north arrow but no coordinate grid. It is a
planning map, not a georeferenced access layer.

MWP #3 Tables 34 and 36 also give the Gavin Lake Demonstration Area AAC
benchmark: 2.4 ha/year clearcut, 3.0 ha/year partial cut, 2.4 ha/year salvage,
7.8 ha/year total on a 478 ha net harvest land base with a 100-year cycle. That
is a public management-plan benchmark, not the legacy model's 80-year clearcut
rotation and not the 4,662.96 ha THLB proxy.

## What is missing

The legacy archive (`AFRF.zip`, SHA-256
`3652c493e21b1834e3e6d9c156f257fa1aa97f019df4672872d08ac1bf703a19`) has an
empty `AFRF/roads/` directory. Its pin sets `useRoutes = false`. Its road-build
script references `Roads_PW_v2.shp` and `Mills_PW.shp` at a legacy Windows path,
but those files were not shipped. The route-report script still names
`Destination.CRB`, but there are no route tables behind it.

The private OneDrive payload contains the Marshal plots, the Kozak taper
package, and the LiDAR products. It contains no road centerlines, mill register,
log price list, scaling record, harvest-system record, or road-cost workbook.

The public BC road layer used for Knife Creek is not a Gavin Lake layer. Gavin
Lake therefore needs an AFRF road inventory or a new digitization with an
explicit accuracy statement.

## Reuse

The engineering template is the nearby TSA23 route extension:

- `config/ws4/route_c5_road.yaml` for the route-account pattern;
- `runtime/ws4/roads_c5/{segments,vertices,destinations,linkages}.csv` for the
  table schema;
- `reports/ws4-road-aware-opt.md` and `reports/ws4-road-aware-attempt.md` for
  the performance envelope; and
- the `ws4.roads` route model for network, destination choice, cost ledger, and
  used-road geometry.

The TSA23 network has 465,263 segments, 72,299 vertices, 102,128 block
linkages, and three mill destinations. It is a useful schema and performance
test. Its mill identities and cost rates are not AFRF values.

The log-grade path is `femic.fmg.patchworks` with the `log-grades` BTC
indicator bank. The shipped price matrices are coastal; Gavin Lake needs an
interior matrix and a species crosswalk.

## Screening result (2026-10-31)

The first Gavin Lake delivered-wood layer is built and recorded in
`data/delivered_wood/gavin/`.

- Public road layer: 69 features, merged into 193 segments, 19.3 km. The plan
  records 112.2 km, so the public layer is incomplete.
- Route graph: 178 components joined by 177 synthetic connectors; 5 candidate
  sawlog mills; median block access 344 m.
- Run: 2,907 fragments, 5,660,337 m3, 57.18 M CAD haul, 0.59 M CAD maintenance.
- All volume goes to `destination.MILL_107_LBR` because no demand or capacity
  constraint is available.
- Sort/value: 683.9 M CAD gross value; Df-Larch sawlog is 2,122,049 m3 and
  264.0 M CAD.

The rates are TSA23 proxies, the mill haul is a straight-line abstraction, and
the sort mix and prices are regional BC references. This is a screening layer.

## Work packages

### P7.1 Source audit and extraction

- Extract the road, harvest-system, and access material from MWP #3.
- Record Table 37, Table 38, section 8.1, section 8.2, and Appendix 11 page
  references.
- Render the Gavin Lake access map and record that it is schematic.
- Inventory the legacy archive and the private OneDrive payload.
- Write the data request and gap list.

Deliverables: `notes/reference/afrf-roads-logs-mills-sources.md`,
`data/roads/source_manifest.json`, and the AFRF data request.

### P7.2 Road network and access topology

- Acquire the AFRF Gavin Lake road centerline or digitize the Appendix 11
  access map with control points and an error report.
- Classify existing, planned, permanent, temporary, active, deactivated, and
  unknown segments.
- Build `vertices`, `segments`, `destinations`, and `linkages`.
- Link each of the 2,907 blocks to one access vertex, with the 400 m skid limit.
- Reconcile to the 112.2 km existing and 136.1 km planned lengths in Table 37.
- Mark blocks beyond the skid limit or outside the planned network as
  unreachable rather than assigning a false access point.

Deliverables: `data/roads/gavinlake/roads.gpkg` and the four route tables.

### P7.3 Mills, destinations, and eligibility

- Build a mill register with name, operator, coordinates, status, capacity,
  accepted species, accepted sorts, and source date.
- Build product-to-destination eligibility.
- Add delivery or capacity constraints only where a source supports them.

Deliverables: `data/mills/mills.csv`, `eligibility.csv`, and
`destinations.csv`.

### P7.4 Log sorts and prices

- Build an interior species-by-grade price matrix with a dated provenance.
- Define the species and grade crosswalk for the Gavin species set.
- Add the matrix through a FEMIC recipe overlay, not by editing the shipped
  coastal matrices.
- Configure `log-grades` products, species splits, and value products.
- Prove that explicit grades sum to harvested volume.

Deliverables: `config/log_prices.afrf.yaml`,
`config/log_grade_species_crosswalk.csv`, and a grade-reconciliation report.

### P7.5 Harvest systems and constraints

- Build slope and access constraints from the best available DEM and road
  layer.
- Classify blocks as shortwood, feller-buncher/grapple, hand-falling/cable, or
  inaccessible.
- Apply the 30% and 60% slope thresholds, the 400 m skid limit, and the
  no-circular-route assumption.
- Add system eligibility to treatments. Add system costs only with a source.
- Keep the legacy clearcut baseline separate from the plan's partial-cut and
  salvage benchmark.

Deliverables: `data/harvest_systems/gavinlake_systems.csv` and
`gavinlake_constraints.gpkg`.

### P7.6 Gavin Lake integration

- Add the route config, mill destinations, log-grade products, and harvest
  system accounts to the Gavin Lake dataset.
- Run the baseline with route accounting and one route-constrained sensitivity.
- Write `route_values.csv`, `network_table.csv`, `route_cost_report.csv`, and
  `used_roads.csv`.
- Serve the source road layer and the used-road overlay.
- Keep the LTSY and growing-stock diagnostics separate from the delivered-wood
  layer.

Deliverables: `ws4/dataset_gavinlake_roads_v1/`, `config/gavinlake_route.yaml`,
and `ws4/runtime/gavinlake_roads_v1/`.

### P7.7 Validation, uncertainty, and publication

- Reconcile road length and area to Table 37.
- Check connectivity, destination eligibility, build-once behavior,
  maintenance, and haul distance.
- Run low/base/high price and cost sensitivities.
- Record the performance envelope for report-only and optimizer use.
- Publish the source note and methods. Do not publish raw private data or claim
  legal access.

Deliverables: `notes/reports/p7-roads-logs-mills-validation.md` and docs pages.

## Data request to AFRF

1. `Roads_PW_v2.shp` and `Mills_PW.shp`, or current equivalents.
2. The legacy route tables: `vertices`, `segments`, `destinations`, and
   `linkages`.
3. Current Gavin Lake road inventory: centerlines, class, surface, status,
   bridges, gates, culverts, deactivation, and right-of-way width.
4. Road construction, maintenance, haul, landing, and deactivation costs.
5. Mill register: name, location, operator, capacity, species and grade
   acceptance, minimum volume, and current status.
6. Log price lists, sales records, scaling records, and grade distributions.
7. Harvest-system records, block prescriptions, slope/terrain data, and
   operational constraints.
8. The current approved plan or order that governs the block.
9. Publication permission for each layer: public, derived, or private-only.

## Risks and controls

| Risk | Control |
| --- | --- |
| No Gavin road layer | Acquire it or digitize with control points and an error report |
| Appendix 11 is schematic | Use it for context only; do not treat a warped raster as a legal layer |
| Legacy model is clearcut-only | Keep the legacy baseline; add the plan's partial-cut and salvage benchmark separately |
| TSA23 rates are not AFRF rates | Reuse schema and code, not numbers |
| Coastal prices are wrong | Build an interior matrix and keep the coast as sensitivity |
| Mill capacity is unknown | Leave capacity unconstrained and mark eligibility unknown |
| Full network is slow | Measure report-only and optimizer cases separately |
| Roads double-count THLB area | Reconcile right-of-way area against the landbase |
| Legal access is unknown | Label the layer as modelled access, not legal access |

## Definition of done

- The source register and gap list are complete.
- Gavin Lake has a road network, route config, mill register, and sort basis, or
  an explicit statement of what is missing.
- The baseline has a delivered-wood run with route and sort accounts.
- The validation report reconciles to Table 37 and states every residual.
- No document presents the result as a statutory AAC, a legal access
  determination, or a legal-compliance finding.

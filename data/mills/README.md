# Candidate mills

`runbooks/build_afrf_mill_candidates.py` builds a candidate mill register from
the BC Major Timber Processing Facilities layer.

Files:

- `bc_mills_source.geojson` - the public BC feature layer, OGL-BC;
- `afrf_mill_candidates.csv` - mills within 100 km of Gavin Lake or Gavin Lake;
- `candidate_destinations.csv` - destination-account candidates; and
- `mills_metadata.json` - source date, radius, counts, and caveats.

The table gives mill location, product class, status, and estimated annual
capacity. It does **not** give accepted log sorts or current log demand.

`candidate_sort` is inferred from the mill product class (`LBR` -> sawlog,
`PLY`/`VNR` -> peeler, `PLP`/`PLT`/`CHP` -> pulpwood, `LGH` -> house log, and
so on). It is a screening label, not a confirmed acceptance rule. Do not build
a product-eligibility table from it without mill confirmation.

The source is a 2023 Mill List Survey published in 2026. Verify current status
and capacity before using it in a decision.

## Historical mill references

`mwp3_historical_mill_references.csv` transcribes the mill references in the
2007 management plan. They are historical: G.W.J. Moore Sawmill at 150 Mile
House, the Gavin Lake bush mills, the All-Fir sawmill at Gavin Lake, the
Merrill-Gardner/Merrill-Wagner sawmill, and generic Williams Lake mills. The
plan gives no current mill names, capacities, accepted sorts, or grade prices.

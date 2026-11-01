# Gavin Lake screening delivered-wood layer

This is the best delivered-wood layer that can be built from the current data.
It is a screening model, not an operational or legal-access model.

## Route network

`route/` contains the four WS4 route tables and `route.yaml`.

- 2,907 legacy fragments.
- 69 public tenure-road features, merged into 193 road segments.
- The public layer is disconnected: 178 components, joined by 177 straight
  synthetic connectors.
- 5 candidate sawlog mills: Tolko Williams Lake (2), West Fraser Williams Lake,
  West Fraser Quesnel, and West Fraser 100 Mile House.
- Block access is a straight line to the nearest public-road vertex. Median
  distance is 344 m; maximum is 2,215 m.
- Mill haul is a straight-line distance times 1.25, not a routed highway path.

Cost rates are TSA23 C5 route-fixture medians used as a proxy:

- haul: 0.00016 CAD per m3 per metre;
- build: 0.00 CAD per metre;
- maintenance: 2.00 CAD per metre per year.

They are not AFRF contract rates.

## Route result

The run is `ws4/runtime/gavin_delivered_wood_screening`, reproduced with:

```bash
python runbooks/build_gavin_screening_route.py \
  --out-dir data/delivered_wood/gavin/route
ws4 simulate \
  --dataset ws4/runtime/legacy_matrix \
  --schedule ws4/schedules/baseline_evenflow.csv \
  --years 300 \
  --route-config data/delivered_wood/gavin/route/route.yaml \
  --out ws4/runtime/gavin_delivered_wood_screening
```

Result:

- 2,907 fragments routed.
- 5,660,337 m3 routed.
- 57.18 M CAD haul.
- 0.59 M CAD maintenance.
- 0 build cost, because all public roads are treated as existing.
- All volume goes to `destination.MILL_107_LBR`; without mill demand or
  capacity constraints, the least-cost mill wins.

## Log sorts and value

`runbooks/build_gavin_delivered_wood.py` splits each fragment's routed volume
using:

- area-weighted species composition from the 2025 VRI for Gavin Lake;
- the BC interior market species groups;
- the June-August 2026 BC Interior Log Market Report sort mix; and
- the published species-group and sort average prices.

The result is 5,660,337 m3 and about 683.9 M CAD gross value. The largest sort is
Df-Larch sawlog at 2,122,049 m3 and 264.0 M CAD. Deciduous and residual species
use the `Other/Other` price as a proxy.

The sort mix is a regional market-purchase mix, not an AFRF grade distribution.
The prices are regional averages, not AFRF sales. This is a screening layer.

The block-level detail file is generated at runtime but not committed because it
is large; the year and mill summaries are committed.

## Files

- `delivered_wood_by_year.csv` - year/mill/species/sort totals.
- `delivered_wood_by_mill.csv` - mill/species/sort totals.
- `delivered_wood_metadata.json` - totals, assumptions, caveats.
- `route_values.csv` - WS4 route output.
- `route_cost_report.csv` - WS4 route cost report.
- `used_roads.csv` - WS4 used-road geometry.
- `route_map.png` - screening route and mill map.

## Limits

- Public road layer is 19.3 km against 112.2 km in MWP #3 Table 37.
- Synthetic connectors and mill haul are not routed roads.
- Mill acceptance, demand, and capacity are not modelled.
- Sort mix and prices are regional BC references, not AFRF records.
- No AAC, legal-access, or legal-compliance claim is made.

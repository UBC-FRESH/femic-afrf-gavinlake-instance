# Interior log-price reference

`runbooks/build_bc_interior_price_reference.py` transcribes two public BC
sources:

- the **BC Interior Log Market Report** for the 3-month period ending
  31 August 2026; and
- the **BC Timber Scaling Manual, Chapter 9, Interior Grading**.

Files:

- `bc_interior_log_market_2026-08.csv` - species-group and sort volumes and
  average prices, CAD/m3;
- `bc_interior_grade_codes.csv` - the five interior grades Z/6/1/2/4;
- `species_crosswalk_candidate.csv` - AFRF species to interior market groups;
- `../../config/log_prices.afrf_candidate.yaml` - a candidate reference
  matrix, explicitly not a FEMIC `log-grades` recipe; and
- `log_prices_metadata.json` - source URLs, hashes, period, and caveats.

The market report gives **species-group and sort averages**, not a mill-specific
accepted-sort list and not a grade-by-grade price matrix. Interior grades are
Z/6/1/2/4, not the coastal D/F/H/I/J/U/X/Y family used by the current FEMIC
`log-grades` recipe.

Do not apply these averages to an AFRF grade volume without a documented
species and grade crosswalk. The report is a regional reference, not an AFRF
sales record.

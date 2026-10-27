# Site index

`klinka_2004_site_index.csv` transcribes Tables 8.2.1–8.2.4 of Klinka et al.
2004, *Site Units of the University of British Columbia Alex Fraser Research
Forest* (PDF pages 62–63, printed 53–54).

The Gavin Lake block is in the SBSdw1 and ICHmk3 units; the table also carries
IDFxm and IDFdk3 for the sibling Knife Creek instance. The columns are:

- `zonal_unit`, `site_series_code`, `site_series_name`;
- `species` — Douglas-fir, lodgepole pine, or hybrid/interior spruce;
- `site_index_m_50` — metres at 50 years breast height;
- `site_index_class` — the report's nominal 5-class scale (1 highest);
- `status` — `viable`, `limited`, or `non-viable`; and
- `note` — limits such as `<9 m` and `19/limited`, kept rather than silently
  converted.

The metadata file records the source PDF SHA-256 and transcription convention.
The report's figures are photographs and flow diagrams, not quantitative
charts; the tables are the right source.

These are potential-productivity estimates, not a measured Gavin growth curve.
Do not replace the legacy H matrix yields with them, and do not infer a site
series from BEC alone.

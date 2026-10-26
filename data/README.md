# Data directory

| Path | Purpose | Git |
| --- | --- | --- |
| `legacy_gavinlake/` | Sanitized legacy H matrix, spatial inventory, topology, pin, scripts | Tracked |
| `downloads/` | Local source downloads | Ignored |
| `raw/` | Local raw archive copies | Ignored |
| `private/` | Restricted data | Ignored, never committed |

Rules:

- Do not edit `legacy_gavinlake/` to make a run pass. Add a derived file.
- Record the archive hash and the transformation.
- Do not commit the raw archive; commit the sanitized package and its
  provenance.
- Do not commit private financial data or machine-specific paths.

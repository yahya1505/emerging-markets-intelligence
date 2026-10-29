# Data Dictionary

This is a high-level guide based on the project files. Verify live PostgreSQL column types, constraints, and view definitions before treating it as a complete database specification.

## Primary observation grain

The cleaned dataset is intended to contain one record per **country × indicator × year**.

| Field | Description |
|---|---|
| `country_code` | Three-letter country code used by the source |
| `country_name` | Country display name |
| `indicator_code` | World Bank indicator identifier |
| `indicator_name` | Human-readable indicator name |
| `business_dimension` | Analytical category assigned by the project |
| `year` | Observation year |
| `value` | Numeric indicator value |
| `unit` | Unit or scale of the indicator |
| `value_status` | Status/availability marker preserved by the pipeline |

The database loader writes these fields to `economic_observations` and uses `(country_code, indicator_code, year)` as the conflict key.

## Indicator catalogue

See [`../data/reference/indicator_catalog.csv`](../data/reference/indicator_catalog.csv) for the authoritative project-level list of codes and units.

| Indicator | World Bank code | Unit |
|---|---|---|
| GDP growth | `NY.GDP.MKTP.KD.ZG` | Annual percent |
| GDP per capita growth | `NY.GDP.PCAP.KD.ZG` | Annual percent |
| Inflation | `FP.CPI.TOTL.ZG` | Annual percent |
| Unemployment | `SL.UEM.TOTL.ZS` | Percent of labor force |
| Current-account balance | `BN.CAB.XOKA.GD.ZS` | Percent of GDP |
| FDI net inflows | `BX.KLT.DINV.WD.GD.ZS` | Percent of GDP |
| Trade | `NE.TRD.GNFS.ZS` | Percent of GDP |

## Reference files

- `data/reference/country_universe.csv`: selected country codes and names.
- `data/reference/indicator_catalog.csv`: indicator codes, display names, units, and business dimensions.

## Database objects

The project references `economic_observations` as the main loaded table. The SQL files define analytical queries and risk-scoring logic. Inspect each SQL script and the live database for exact views and output columns before documenting additional objects as guaranteed.

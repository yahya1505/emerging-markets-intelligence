# Data Quality and Limitations

## Pipeline validation

The pipeline is orchestrated by `run_pipeline.py` in this order:

1. Extract from the World Bank API.
2. Validate the extracted dataset.
3. Transform and standardize the data.
4. Validate the cleaned dataset.
5. Load cleaned observations into PostgreSQL.

The validation scripts check dataset structure and coverage; inspect their output and the generated reports after each run.

## Quality controls to review

- API response status and retry handling.
- Expected country × indicator × year coverage.
- Duplicate `(country_code, indicator_code, year)` keys.
- Missing values and extraction status.
- Numeric conversion and unit preservation.
- Year range and country/indicator coverage.
- Reconciliation of cleaned CSV row counts with database rows.

The loader checks for duplicate keys in the CSV and uses an `ON CONFLICT ... DO UPDATE` statement for the observation key. It also compares the total database row count with the submitted row count; that check assumes the target table contains only the expected project observations.

## Missing values

Missing values must remain distinguishable from zero. Zero can be a valid economic observation; missing means an observation is unavailable or unreported. Any imputation or filtering should be documented explicitly.

## Limitations

- The country universe is a selected set of 20 economies.
- Scores depend on the peer group, period, and selected weights.
- The score is not an official rating or validated prediction.
- Historical heatmap thresholds are project-specific display rules.
- World Bank values may be revised and definitions can vary by country and indicator.
- Historical association does not establish causality.

## Publication checklist

- [ ] Re-run the pipeline and review the latest logs and quality reports.
- [ ] Confirm duplicate and missing-value counts.
- [ ] Verify indicator codes, names, units, and source URLs.
- [ ] Check that SQL outputs agree with the published methodology.
- [ ] Test report slicers, interactions, tooltips, and conditional formatting.
- [ ] Remove credentials, logs, local paths, and temporary files.
- [ ] Add genuine report screenshots.

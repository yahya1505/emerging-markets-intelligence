# Project Brief

## Objective

Build a repeatable data pipeline and interactive dashboard to compare macroeconomic growth and relative vulnerability across selected economies.

## Scope

- 20 selected countries.
- Historical period: 2005–2024.
- Baseline risk-scoring period: 2020–2024.
- Initial source: World Bank Indicators API.
- Seven indicators: GDP growth, GDP per capita growth, inflation, unemployment, current-account balance, FDI net inflows, and trade (% of GDP).
- Python and pandas for extraction, transformation, and validation.
- PostgreSQL for persistent storage and SQL analytics.
- Power BI for visual analysis.

## Business questions

1. Which countries show relatively strong economic growth?
2. Which countries exhibit potential macroeconomic pressure?
3. How does each country compare with its peers?
4. Which countries warrant further research?

## Deliverables

- Python data pipeline.
- Raw and processed extracts.
- Data-quality reports.
- PostgreSQL analytical tables/views.
- Power BI report.
- Methodology and reproducibility documentation.

## Limitations

- Country selection is defined for this project.
- Data availability varies by indicator, country, and year.
- Missing values must not be interpreted as zero.
- Exploratory risk scores are not official ratings or validated crisis predictions.

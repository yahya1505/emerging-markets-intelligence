
-- Project: Emerging Markets Intelligence & Risk Monitor
-- Analysis: Average GDP Growth and Inflation
-- Period: 2020-2024
-- Purpose: Compare economic growth and price stability across countries.

SELECT
    country_name,
    ROUND(
        AVG(value) FILTER (
            WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
        ),
        2
    ) AS avg_gdp_growth_pct,
    ROUND(
        AVG(value) FILTER (
            WHERE indicator_code = 'FP.CPI.TOTL.ZG'
        ),
        2
    ) AS avg_inflation_pct,
    COUNT(value) FILTER (
        WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
    ) AS gdp_years_available,
    COUNT(value) FILTER (
        WHERE indicator_code = 'FP.CPI.TOTL.ZG'
    ) AS inflation_years_available
FROM economic_observations
WHERE year BETWEEN 2020 AND 2024
  AND indicator_code IN (
      'NY.GDP.MKTP.KD.ZG',
      'FP.CPI.TOTL.ZG'
  )
GROUP BY country_code, country_name
ORDER BY avg_gdp_growth_pct DESC;

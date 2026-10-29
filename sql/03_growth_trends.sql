
-- Project: Emerging Markets Intelligence & Risk Monitor
-- Analysis: Annual GDP Growth Trends
-- Period: 2020-2024

SELECT
    country_name,
    year,
    ROUND(value, 2) AS gdp_growth_pct
FROM economic_observations
WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
  AND year BETWEEN 2020 AND 2024
ORDER BY country_name, year;

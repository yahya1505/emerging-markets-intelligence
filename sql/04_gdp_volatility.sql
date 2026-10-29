
-- GDP Growth: Average, Volatility, and Minimum
-- Period: 2020-2024

SELECT
    country_name,
    COUNT(value) AS years_available,
    ROUND(AVG(value), 2) AS avg_gdp_growth_pct,
    ROUND(STDDEV_SAMP(value), 2) AS gdp_growth_volatility,
    ROUND(MIN(value), 2) AS min_gdp_growth_pct
FROM economic_observations
WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
  AND year BETWEEN 2020 AND 2024
GROUP BY country_code, country_name
ORDER BY gdp_growth_volatility DESC;

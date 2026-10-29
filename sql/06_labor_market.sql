
-- Project: Emerging Markets Intelligence & Risk Monitor
-- Analysis: Labor Market Conditions
-- Period: 2020-2024

SELECT
    country_name,
    ROUND(AVG(value), 2) AS avg_unemployment_pct,
    ROUND(MAX(value) FILTER (WHERE year = 2020), 2) AS unemployment_2020_pct,
    ROUND(MAX(value) FILTER (WHERE year = 2024), 2) AS unemployment_2024_pct,
    ROUND(
        MAX(value) FILTER (WHERE year = 2024)
        - MAX(value) FILTER (WHERE year = 2020),
        2
    ) AS unemployment_change_pp
FROM economic_observations
WHERE indicator_code = 'SL.UEM.TOTL.ZS'
  AND year BETWEEN 2020 AND 2024
GROUP BY country_code, country_name
ORDER BY unemployment_change_pp DESC;

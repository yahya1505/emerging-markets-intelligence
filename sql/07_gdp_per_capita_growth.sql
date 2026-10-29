
-- Project: Emerging Markets Intelligence & Risk Monitor
-- Analysis: GDP per Capita Growth
-- Period: 2020-2024

SELECT
    country_name,
    COUNT(value) AS years_available,
    ROUND(AVG(value), 2) AS avg_gdp_per_capita_growth_pct,
    ROUND(
        MAX(value) FILTER (WHERE year = 2020),
        2
    ) AS growth_2020_pct,
    ROUND(
        MAX(value) FILTER (WHERE year = 2024),
        2
    ) AS growth_2024_pct
FROM economic_observations
WHERE indicator_code = 'NY.GDP.PCAP.KD.ZG'
  AND year BETWEEN 2020 AND 2024
GROUP BY country_code, country_name
ORDER BY avg_gdp_per_capita_growth_pct DESC;

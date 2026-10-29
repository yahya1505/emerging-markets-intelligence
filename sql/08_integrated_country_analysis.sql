
-- Project: Emerging Markets Intelligence & Risk Monitor
-- Analysis: Integrated Country-Level Economic Indicators
-- Period: 2020-2024

SELECT
    country_code,
    country_name,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
    ), 2) AS avg_gdp_growth_pct,

    ROUND(STDDEV_SAMP(value) FILTER (
        WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
    ), 2) AS gdp_growth_volatility,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'NY.GDP.PCAP.KD.ZG'
    ), 2) AS avg_gdp_per_capita_growth_pct,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'FP.CPI.TOTL.ZG'
    ), 2) AS avg_inflation_pct,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'SL.UEM.TOTL.ZS'
    ), 2) AS avg_unemployment_pct,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'BN.CAB.XOKA.GD.ZS'
    ), 2) AS avg_current_account_pct_gdp,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'BX.KLT.DINV.WD.GD.ZS'
    ), 2) AS avg_fdi_inflows_pct_gdp,

    ROUND(AVG(value) FILTER (
        WHERE indicator_code = 'NE.TRD.GNFS.ZS'
    ), 2) AS avg_trade_pct_gdp

FROM economic_observations
WHERE year BETWEEN 2020 AND 2024
GROUP BY country_code, country_name
ORDER BY avg_gdp_growth_pct DESC;

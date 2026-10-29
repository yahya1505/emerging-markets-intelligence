
CREATE OR REPLACE VIEW vw_country_risk_scores AS

WITH country_metrics AS (
    SELECT
        economic_observations.country_code,
        economic_observations.country_name,

        AVG(economic_observations.value) FILTER (
            WHERE economic_observations.indicator_code = 'NY.GDP.MKTP.KD.ZG'
        ) AS avg_gdp_growth,

        STDDEV_POP(economic_observations.value) FILTER (
            WHERE economic_observations.indicator_code = 'NY.GDP.MKTP.KD.ZG'
        ) AS gdp_growth_volatility,

        AVG(economic_observations.value) FILTER (
            WHERE economic_observations.indicator_code = 'FP.CPI.TOTL.ZG'
        ) AS avg_inflation,

        AVG(economic_observations.value) FILTER (
            WHERE economic_observations.indicator_code = 'BN.CAB.XOKA.GD.ZS'
        ) AS avg_current_account,

        AVG(economic_observations.value) FILTER (
            WHERE economic_observations.indicator_code = 'BX.KLT.DINV.WD.GD.ZS'
        ) AS avg_fdi

    FROM economic_observations

    WHERE economic_observations.indicator_code IN (
        'NY.GDP.MKTP.KD.ZG',
        'FP.CPI.TOTL.ZG',
        'BN.CAB.XOKA.GD.ZS',
        'BX.KLT.DINV.WD.GD.ZS'
    )
    AND economic_observations.year BETWEEN 2020 AND 2024
    AND economic_observations.value_status = 'available'

    GROUP BY
        economic_observations.country_code,
        economic_observations.country_name

    HAVING COUNT(*) FILTER (
        WHERE economic_observations.indicator_code = 'NY.GDP.MKTP.KD.ZG'
    ) = 5
    AND COUNT(*) FILTER (
        WHERE economic_observations.indicator_code = 'FP.CPI.TOTL.ZG'
    ) = 5
    AND COUNT(*) FILTER (
        WHERE economic_observations.indicator_code = 'BN.CAB.XOKA.GD.ZS'
    ) = 5
    AND COUNT(*) FILTER (
        WHERE economic_observations.indicator_code = 'BX.KLT.DINV.WD.GD.ZS'
    ) = 5
),

ranked_metrics AS (
    SELECT
        country_metrics.*,

        100 * (
            1 - PERCENT_RANK() OVER (
                ORDER BY avg_gdp_growth
            )
        ) AS growth_risk_score,

        100 * PERCENT_RANK() OVER (
            ORDER BY avg_inflation
        ) AS inflation_risk_score,

        100 * PERCENT_RANK() OVER (
            ORDER BY gdp_growth_volatility
        ) AS volatility_risk_score,

        100 * (
            1 - PERCENT_RANK() OVER (
                ORDER BY avg_current_account
            )
        ) AS external_risk_score

    FROM country_metrics
),

final_scores AS (
    SELECT
        ranked_metrics.*,

        (
            growth_risk_score / 6.0
            + volatility_risk_score / 6.0
            + inflation_risk_score / 3.0
            + external_risk_score / 3.0
        ) AS overall_risk_score

    FROM ranked_metrics
)

SELECT
    country_code,
    country_name,
    2020 AS analysis_start_year,
    2024 AS analysis_end_year,

    avg_gdp_growth,
    gdp_growth_volatility,
    avg_inflation,
    avg_current_account,
    avg_fdi,

    growth_risk_score,
    volatility_risk_score,
    inflation_risk_score,
    external_risk_score,
    overall_risk_score,

    RANK() OVER (
        ORDER BY overall_risk_score DESC
    ) AS risk_rank

FROM final_scores;

# Macro-Economic Risk Scoring Methodology

## 1. Objective

The score compares relative macroeconomic vulnerability across 20 selected emerging and developing economies. The baseline period is **2020–2024**.

It is an exploratory analytical tool for peer comparison, not an official sovereign credit rating or a prediction of crisis probability.

## 2. Indicators and direction

| Indicator | Role in the model | Risk direction |
|---|---|---|
| Average GDP growth | Composite score | Lower growth = higher relative risk |
| GDP growth volatility | Composite score | Higher volatility = higher relative risk |
| Average inflation | Composite score | Higher inflation = higher relative risk |
| Average current-account balance (% of GDP) | Composite score | Lower balance = higher relative risk |
| FDI net inflows (% of GDP) | Supporting context | Not included in composite score |

FDI is retained as supporting context because its relationship with risk is not unambiguously positive or negative.

## 3. Weights

The composite score groups the four scoring indicators into three dimensions:

| Dimension | Indicator | Weight |
|---|---|---:|
| Growth and resilience | Average GDP growth | 16.67% |
| Growth and resilience | GDP growth volatility | 16.67% |
| Price stability | Average inflation | 33.33% |
| External vulnerability | Current-account balance | 33.33% |
| **Total** | | **100.00%** |

The dimensions receive approximately equal weights. Growth and volatility split the weight assigned to growth and resilience so that this dimension does not receive extra weight merely because it contains two indicators. These weights are a transparent baseline assumption, not an empirically proven optimal scheme.

## 4. Period and coverage

- Scoring period: 2020–2024.
- Country universe: 20 selected economies.
- Each country is expected to have five annual observations for each scoring indicator.
- Countries with incomplete coverage may be excluded from the scoring output, depending on the SQL implementation.

## 5. Normalization and composite score

The SQL model uses PostgreSQL `PERCENT_RANK()` to convert indicator values into relative scores across the selected country sample, with risk direction taken into account.

Conceptually:

```text
Overall Risk Score =
    (1/6 × Growth Risk Score)
  + (1/6 × Volatility Risk Score)
  + (1/3 × Inflation Risk Score)
  + (1/3 × External Risk Score)
```

The score ranges from 0 to 100 under the implemented normalization. A score of 100 indicates the highest relative risk position for the composite model within the selected sample; it does not indicate a 100% probability of crisis.

## 6. Sensitivity scenarios

The project SQL includes alternative weighting scenarios for sensitivity analysis:

| Scenario | Growth | Volatility | Inflation | External |
|---|---:|---:|---:|---:|
| Baseline | 16.67% | 16.67% | 33.33% | 33.33% |
| Inflation priority | 12.5% | 12.5% | 50% | 25% |
| External priority | 12.5% | 12.5% | 25% | 50% |

These scenarios help assess how sensitive relative rankings are to alternative weighting assumptions. They do not establish that any one scenario is universally superior.

## 7. Historical heatmap

The historical-trends heatmap uses indicator-specific conditional-formatting rules that are separate from the composite risk score. These colors are exploratory visual cues, not universal economic thresholds. Check the current Power BI DAX and report formatting for the exact active rules before interpreting individual cells.

## 8. Limitations

1. Scores are relative to the selected countries and period.
2. Percentile scores can change when the sample or analysis period changes.
3. Current-account deficits are not inherently unsustainable; interpretation depends on financing, reserves, and external debt.
4. High GDP growth does not necessarily imply low risk.
5. FDI inflows do not automatically offset external vulnerabilities.
6. The model excludes government debt, reserves, debt-service burdens, institutional quality, and political risk.
7. The model has not been validated against historical crisis or sovereign-default outcomes.
8. The score should support further investigation, not replace country-specific research.

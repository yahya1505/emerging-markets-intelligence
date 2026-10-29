
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "world_bank_observations.csv"
)
INDICATOR_FILE = (
    PROJECT_ROOT / "data" / "reference"
    / "indicator_catalog.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "world_bank_clean.csv"
)
REPORT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "data_completeness_report.csv"
)

# 1. Load source data and indicator metadata
data = pd.read_csv(DATA_FILE)
indicators = pd.read_csv(INDICATOR_FILE)

# 2. Standardize data types
data["country_code"] = data["country_code"].astype(str).str.strip()
data["indicator_code"] = data["indicator_code"].astype(str).str.strip()
data["year"] = pd.to_numeric(data["year"], errors="raise").astype(int)
data["value"] = pd.to_numeric(data["value"], errors="coerce")

# 3. Enrich observations with indicator metadata
clean_data = data.merge(
    indicators,
    on="indicator_code",
    how="left",
    validate="many_to_one",
    indicator=True,
)

unmatched_indicators = clean_data[
    clean_data["_merge"] != "both"
]

if not unmatched_indicators.empty:
    raise ValueError("Some indicator codes are missing from the catalog.")

clean_data = clean_data.drop(columns=["_merge", "indicator_name_x"])
clean_data = clean_data.rename(
    columns={"indicator_name_y": "indicator_name"}
)

# 4. Add a transparent availability flag
clean_data["value_status"] = clean_data["value"].apply(
    lambda value: "available" if pd.notna(value) else "missing"
)

# 5. Arrange columns for downstream analysis
column_order = [
    "country_code",
    "country_name",
    "indicator_code",
    "indicator_name",
    "business_dimension",
    "year",
    "value",
    "unit",
    "value_status",
]

clean_data = clean_data[column_order].sort_values(
    ["country_code", "indicator_code", "year"]
)

# 6. Build completeness report for each country-indicator pair
completeness = (
    clean_data.groupby(
        [
            "country_code",
            "country_name",
            "indicator_code",
            "indicator_name",
        ],
        dropna=False,
    )
    .agg(
        expected_years=("year", "size"),
        available_values=("value", "count"),
        missing_values=("value", lambda values: values.isna().sum()),
        first_year=("year", "min"),
        last_year=("year", "max"),
    )
    .reset_index()
)

completeness["completeness_pct"] = (
    completeness["available_values"]
    / completeness["expected_years"]
    * 100
).round(2)

# 7. Save outputs
clean_data.to_csv(OUTPUT_FILE, index=False)
completeness.to_csv(REPORT_FILE, index=False)

print("=== TRANSFORMATION SUMMARY ===")
print(f"Rows transformed: {len(clean_data)}")
print(f"Columns in clean dataset: {len(clean_data.columns)}")
print(f"Available values: {clean_data['value'].count()}")
print(f"Missing values: {clean_data['value'].isna().sum()}")
print(f"Clean dataset saved: {OUTPUT_FILE}")
print(f"Completeness report saved: {REPORT_FILE}")

print("\n=== COMPLETENESS OVERVIEW ===")
print(
    completeness["completeness_pct"]
    .describe()
    .round(2)
    .to_string()
)

print("\nTransformation completed.")

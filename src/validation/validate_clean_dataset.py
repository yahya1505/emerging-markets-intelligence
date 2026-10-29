
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "world_bank_clean.csv"
)
COUNTRY_FILE = (
    PROJECT_ROOT / "data" / "reference"
    / "country_universe.csv"
)
INDICATOR_FILE = (
    PROJECT_ROOT / "data" / "reference"
    / "indicator_catalog.csv"
)

data = pd.read_csv(DATA_FILE)
countries = pd.read_csv(COUNTRY_FILE)
indicators = pd.read_csv(INDICATOR_FILE)

required_columns = [
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

duplicate_count = data.duplicated(
    subset=["country_code", "indicator_code", "year"]
).sum()

missing_required_columns = sorted(
    set(required_columns) - set(data.columns)
)

missing_keys = data[
    ["country_code", "indicator_code", "year"]
].isna().sum().sum()

invalid_status = (
    data["value_status"]
    != data["value"].notna().map(
        {True: "available", False: "missing"}
    )
).sum()

unexpected_countries = sorted(
    set(data["country_code"]) - set(countries["country_code"])
)

unexpected_indicators = sorted(
    set(data["indicator_code"]) - set(indicators["indicator_code"])
)

checks = {
    "Expected row count": len(data) == 2800,
    "Expected country count": data["country_code"].nunique() == 20,
    "Expected indicator count": data["indicator_code"].nunique() == 7,
    "Expected year range": (
        data["year"].min() == 2005
        and data["year"].max() == 2024
    ),
    "No duplicate observations": duplicate_count == 0,
    "No missing required columns": len(missing_required_columns) == 0,
    "No missing key fields": missing_keys == 0,
    "Value status is consistent": invalid_status == 0,
    "No unexpected countries": len(unexpected_countries) == 0,
    "No unexpected indicators": len(unexpected_indicators) == 0,
    "Indicator metadata complete": (
        data[["indicator_name", "unit", "business_dimension"]]
        .notna()
        .all()
        .all()
    ),
        "All country-indicator pairs have 20 years": (
        data.groupby(["country_code", "indicator_code"])["year"]
        .nunique()
        .eq(20)
        .all()
    ),
    "Every year is represented for each pair": (
        data.groupby(["country_code", "indicator_code"])["year"]
        .apply(lambda years: set(years) == set(range(2005, 2025)))
        .all()
    ),
}

print("=== CLEAN DATASET VALIDATION ===")
print(f"Rows: {len(data)}")
print(f"Columns: {len(data.columns)}")
print(f"Duplicate observations: {duplicate_count}")
print(f"Missing key fields: {missing_keys}")
print(f"Missing required columns: {missing_required_columns}")
print(f"Unexpected countries: {unexpected_countries}")
print(f"Unexpected indicators: {unexpected_indicators}")

print("\n=== CHECK RESULTS ===")
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'} - {name}")

if all(checks.values()):
    print("\nVALIDATION PASSED")
else:
    print("\nVALIDATION FAILED")
    raise SystemExit(1)
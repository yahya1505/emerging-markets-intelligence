
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "world_bank_observations.csv"
)
COUNTRY_FILE = (
    PROJECT_ROOT / "data" / "reference"
    / "country_universe.csv"
)
INDICATOR_FILE = (
    PROJECT_ROOT / "data" / "reference"
    / "indicator_catalog.csv"
)
STATUS_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "extraction_status.csv"
)

data = pd.read_csv(DATA_FILE)
countries = pd.read_csv(COUNTRY_FILE)
indicators = pd.read_csv(INDICATOR_FILE)
status = pd.read_csv(STATUS_FILE)

print("=== DATASET VALIDATION ===")
print(f"Total rows: {len(data)}")
print(f"Unique countries: {data['country_code'].nunique()}")
print(f"Unique indicators: {data['indicator_code'].nunique()}")
print(f"Minimum year: {data['year'].min()}")
print(f"Maximum year: {data['year'].max()}")

duplicate_count = data.duplicated(
    subset=["country_code", "indicator_code", "year"]
).sum()

missing_values = data[
    ["country_code", "indicator_code", "year", "value"]
].isna().sum()

unexpected_countries = sorted(
    set(data["country_code"]) - set(countries["country_code"])
)
unexpected_indicators = sorted(
    set(data["indicator_code"]) - set(indicators["indicator_code"])
)

out_of_range = (
    (data["year"] < 2005) | (data["year"] > 2024)
).sum()

failed_tasks = (status["status"] == "error").sum()

expected_combinations = len(countries) * len(indicators)
actual_combinations = data[
    ["country_code", "indicator_code"]
].drop_duplicates().shape[0]

print(f"\nDuplicate country-indicator-year rows: {duplicate_count}")
print("\nMissing values:")
print(missing_values.to_string())
print(f"\nUnexpected countries: {unexpected_countries}")
print(f"Unexpected indicators: {unexpected_indicators}")
print(f"Out-of-range year rows: {out_of_range}")
print(f"Failed extraction tasks: {failed_tasks}")
print(
    f"Country-indicator combinations: "
    f"{actual_combinations}/{expected_combinations}"
)

checks = {
    "Expected country count": (
        data["country_code"].nunique() == len(countries)
    ),
    "Expected indicator count": (
        data["indicator_code"].nunique() == len(indicators)
    ),
    "No duplicate records": duplicate_count == 0,
    "No missing key/value fields": (
        missing_values.sum() == 0
    ),
    "No unexpected countries": len(unexpected_countries) == 0,
    "No unexpected indicators": len(unexpected_indicators) == 0,
    "Years within 2005-2024": out_of_range == 0,
    "All extraction tasks resolved": failed_tasks == 0,
    "All combinations represented": (
        actual_combinations == expected_combinations
    ),
}

print("\n=== CHECK RESULTS ===")
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'} - {name}")

if all(checks.values()):
    print("\nVALIDATION PASSED")
else:
    print("\nVALIDATION FAILED")
    raise SystemExit(1)
	
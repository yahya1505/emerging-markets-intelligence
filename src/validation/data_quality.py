
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "indonesia_gdp_growth_2005_2024.csv"
)


def validate_data(data):
    errors = []

    required_columns = [
        "country_code",
        "indicator_code",
        "year",
        "value"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        return errors

    # Pastikan tahun dapat diperlakukan sebagai angka.
    if not pd.api.types.is_integer_dtype(data["year"]):
        errors.append("Year column must contain integers.")

    # Satu observasi untuk setiap negara, indikator, dan tahun.
    duplicate_count = data.duplicated(
        subset=["country_code", "indicator_code", "year"]
    ).sum()

    if duplicate_count > 0:
        errors.append(f"Duplicate records: {duplicate_count}")

    # Periksa rentang tahun.
    if not data["year"].between(2005, 2024).all():
        errors.append("Year outside the expected range.")

    # Nilai boleh kosong, tetapi jika terisi harus numerik.
    non_null_values = data["value"].dropna()

    if not pd.api.types.is_numeric_dtype(non_null_values):
        errors.append("Value column must be numeric.")

    return errors


if __name__ == "__main__":
    data = pd.read_csv(DATA_PATH)

    errors = validate_data(data)

    print(f"Rows checked: {len(data)}")
    print(f"Unique years: {data['year'].nunique()}")
    print(f"Year range: {data['year'].min()}–{data['year'].max()}")
    print(f"Duplicate records: {data.duplicated(subset=['country_code', 'indicator_code', 'year']).sum()}")
    print(f"Missing values: {data['value'].isna().sum()}")

    if errors:
        print("\nVALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nVALIDATION PASSED")


import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "https://api.worldbank.org/v2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def fetch_indicator(country_code, indicator_code, start_year, end_year):
    url = (
        f"{BASE_URL}/country/{country_code}"
        f"/indicator/{indicator_code}"
    )

    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": 100
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Unexpected API response: {payload}")

    metadata, observations = payload

    if not observations:
        raise ValueError("API returned no observations.")

    rows = []

    for observation in observations:
        rows.append({
            "country_code": observation["countryiso3code"],
            "country_name": observation["country"]["value"],
            "indicator_code": observation["indicator"]["id"],
            "indicator_name": observation["indicator"]["value"],
            "year": int(observation["date"]),
            "value": observation["value"],
            "source": "World Bank Indicators API",
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat()
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    data = fetch_indicator(
        country_code="IDN",
        indicator_code="NY.GDP.MKTP.KD.ZG",
        start_year=2005,
        end_year=2024
    )

    raw_path = RAW_DIR / "indonesia_gdp_growth_2005_2024.csv"
    processed_path = (
        PROCESSED_DIR / "indonesia_gdp_growth_2005_2024.csv"
    )

    # Simpan hasil ekstraksi sebagai raw dataset.
    data.to_csv(raw_path, index=False)

    # Untuk tahap awal, data processed sama dengan data raw.
    # Pembersihan dan validasi akan kita tambahkan berikutnya.
    data.to_csv(processed_path, index=False)

    print("Extraction successful!")
    print(f"Rows retrieved: {len(data)}")
    print(f"Year range: {data['year'].min()}–{data['year'].max()}")
    print(f"Missing values: {data['value'].isna().sum()}")
    print("\nPreview:")
    print(data.head())
    print(f"\nRaw file: {raw_path}")
    print(f"Processed file: {processed_path}")

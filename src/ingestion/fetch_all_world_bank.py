
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.worldbank.org/v2"
START_YEAR = 2005
END_YEAR = 2024
PER_PAGE = 100

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_API_DIR = RAW_DIR / "api_responses"


def fetch_indicator(session, country_code, indicator_code):
    url = (
        f"{BASE_URL}/country/{country_code}"
        f"/indicator/{indicator_code}"
    )

    params = {
        "date": f"{START_YEAR}:{END_YEAR}",
        "format": "json",
        "per_page": PER_PAGE,
        "page": 1
    }

    all_observations = []
    raw_pages = []
    errors = []

    while True:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list) or len(payload) < 2:
            raise ValueError(f"Unexpected API response: {url}")

        metadata, observations = payload
        raw_pages.append(payload)

        if observations:
            all_observations.extend(observations)

        total_pages = int(metadata.get("pages") or 1)

        if params["page"] >= total_pages:
            break

        params["page"] += 1

    return all_observations, raw_pages


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_API_DIR.mkdir(parents=True, exist_ok=True)

    countries = pd.read_csv(
        REFERENCE_DIR / "country_universe.csv",
        dtype={"country_code": str}
    )

    indicators = pd.read_csv(
        REFERENCE_DIR / "indicator_catalog.csv",
        dtype={"indicator_code": str}
    )

    session = requests.Session()
    session.headers.update({
        "User-Agent": "EmergingMarketsIntelligencePortfolio/1.0"
    })

    all_rows = []
    status_rows = []

    total_tasks = len(countries) * len(indicators)
    task_number = 0

    for _, country in countries.iterrows():
        for _, indicator in indicators.iterrows():
            task_number += 1

            country_code = country["country_code"]
            indicator_code = indicator["indicator_code"]

            print(
                f"[{task_number}/{total_tasks}] "
                f"{country_code} - {indicator_code}"
            )

            try:
                observations, raw_pages = fetch_indicator(
                    session,
                    country_code,
                    indicator_code
                )

                # Simpan respons API asli untuk audit dan penelusuran.
                raw_file = (
                    RAW_API_DIR
                    / f"{country_code}_{indicator_code}.json"
                )

                with raw_file.open("w", encoding="utf-8") as file:
                    json.dump(
                        raw_pages,
                        file,
                        ensure_ascii=False,
                        indent=2
                    )

                retrieved_at = datetime.now(
                    timezone.utc
                ).isoformat()

                for observation in observations:
                    all_rows.append({
                        "country_code": observation["countryiso3code"],
                        "country_name": observation["country"]["value"],
                        "indicator_code": observation["indicator"]["id"],
                        "indicator_name": observation["indicator"]["value"],
                        "year": int(observation["date"]),
                        "value": observation["value"],
                        "source": "World Bank Indicators API",
                        "retrieved_at_utc": retrieved_at
                    })

                status_rows.append({
                    "country_code": country_code,
                    "indicator_code": indicator_code,
                    "status": (
                        "success" if observations else "no_data"
                    ),
                    "observations": len(observations),
                    "error": ""
                })

            except (requests.RequestException, ValueError, KeyError) as error:
                status_rows.append({
                    "country_code": country_code,
                    "indicator_code": indicator_code,
                    "status": "error",
                    "observations": 0,
                    "error": str(error)
                })

                print(f"  ERROR: {error}")

            # Beri jeda kecil antarpermintaan API.
            time.sleep(0.1)

    columns = [
        "country_code",
        "country_name",
        "indicator_code",
        "indicator_name",
        "year",
        "value",
        "source",
        "retrieved_at_utc"
    ]

    data = pd.DataFrame(all_rows, columns=columns)

    if not data.empty:
        data = data.sort_values(
            ["country_code", "indicator_code", "year"]
        ).reset_index(drop=True)

    status = pd.DataFrame(status_rows)

    data.to_csv(
        RAW_DIR / "world_bank_observations.csv",
        index=False
    )

    data.to_csv(
        PROCESSED_DIR / "world_bank_observations.csv",
        index=False
    )

    status.to_csv(
        PROCESSED_DIR / "extraction_status.csv",
        index=False
    )

    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Configured countries: {len(countries)}")
    print(f"Configured indicators: {len(indicators)}")
    print(f"Combination attempts: {total_tasks}")
    print(f"Observation rows: {len(data)}")
    print(f"Successful combinations: {(status['status'] == 'success').sum()}")
    print(f"Combinations without data: {(status['status'] == 'no_data').sum()}")
    print(f"Failed combinations: {(status['status'] == 'error').sum()}")
    print(f"Countries retrieved: {data['country_code'].nunique()}")
    print(f"Indicators retrieved: {data['indicator_code'].nunique()}")
    print(f"Raw API responses: {RAW_API_DIR}")
    print(f"Processed dataset: {PROCESSED_DIR / 'world_bank_observations.csv'}")
    if (status["status"] == "error").any():
        raise SystemExit(
            "Extraction failed for one or more country-indicator combinations. "
            "Check data/processed/extraction_status.csv and retry failed tasks."
        )
    session.close()


if __name__ == "__main__":
    main()

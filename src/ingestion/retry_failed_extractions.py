
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.worldbank.org/v2"
START_YEAR = 2005
END_YEAR = 2024
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_API_DIR = PROJECT_ROOT / "data" / "raw" / "api_responses"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

STATUS_FILE = PROCESSED_DIR / "extraction_status.csv"
DATA_FILE = PROCESSED_DIR / "world_bank_observations.csv"
RAW_DATA_FILE = RAW_DIR / "world_bank_observations.csv"


def fetch_with_retry(session, country_code, indicator_code, max_attempts=3):
    url = (
        f"{BASE_URL}/country/{country_code}"
        f"/indicator/{indicator_code}"
    )
    params = {
        "date": f"{START_YEAR}:{END_YEAR}",
        "format": "json",
        "per_page": 100,
        "page": 1,
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = session.get(url, params=params, timeout=60)
            response.raise_for_status()
            payload = response.json()

            if (
                not isinstance(payload, list)
                or len(payload) < 2
                or not isinstance(payload[1], list)
            ):
                raise ValueError("Unexpected World Bank API response")

            metadata, observations = payload

            if metadata.get("message"):
                raise ValueError(str(metadata["message"]))

            raw_pages = [payload]
            total_pages = int(metadata.get("pages") or 1)

            for page in range(2, total_pages + 1):
                page_params = {**params, "page": page}
                page_response = session.get(
                    url, params=page_params, timeout=60
                )
                page_response.raise_for_status()
                page_payload = page_response.json()

                if (
                    not isinstance(page_payload, list)
                    or len(page_payload) < 2
                    or not isinstance(page_payload[1], list)
                ):
                    raise ValueError("Unexpected paginated API response")

                raw_pages.append(page_payload)
                observations.extend(page_payload[1])

            return observations, raw_pages

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            print(
                f"  Attempt {attempt}/{max_attempts} failed: {error}"
            )
            if attempt < max_attempts:
                time.sleep(2 * attempt)

    raise RuntimeError(
        f"Failed after {max_attempts} attempts"
    )


def main():
    status = pd.read_csv(STATUS_FILE, dtype=str)
    data = pd.read_csv(DATA_FILE)
    raw_data = pd.read_csv(RAW_DATA_FILE)

    failed = status[status["status"] == "error"].copy()

    if failed.empty:
        print("No failed combinations to retry.")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "EmergingMarketsIntelligencePortfolio/1.0"
    })

    for _, task in failed.iterrows():
        country_code = task["country_code"]
        indicator_code = task["indicator_code"]

        print(f"\nRetrying {country_code} - {indicator_code}")

        try:
            observations, raw_pages = fetch_with_retry(
                session, country_code, indicator_code
            )

            raw_file = (
                RAW_API_DIR / f"{country_code}_{indicator_code}.json"
            )
            with raw_file.open("w", encoding="utf-8") as file:
                import json
                json.dump(raw_pages, file, ensure_ascii=False, indent=2)

            retrieved_at = datetime.now(timezone.utc).isoformat()
            new_rows = []

            for observation in observations:
                new_rows.append({
                    "country_code": observation["countryiso3code"],
                    "country_name": observation["country"]["value"],
                    "indicator_code": observation["indicator"]["id"],
                    "indicator_name": observation["indicator"]["value"],
                    "year": int(observation["date"]),
                    "value": observation["value"],
                    "source": "World Bank Indicators API",
                    "retrieved_at_utc": retrieved_at,
                })

            data = data[
                ~(
                    (data["country_code"] == country_code)
                    & (data["indicator_code"] == indicator_code)
                )
            ]
            if new_rows:
                data = pd.concat(
                    [data, pd.DataFrame(new_rows)],
                    ignore_index=True,
                )

            raw_data = raw_data[
                ~(
                    (raw_data["country_code"] == country_code)
                    & (raw_data["indicator_code"] == indicator_code)
                )
            ]
            if new_rows:
                raw_data = pd.concat(
                    [raw_data, pd.DataFrame(new_rows)],
                    ignore_index=True,
                )

            mask = (
                (status["country_code"] == country_code)
                & (status["indicator_code"] == indicator_code)
            )
            status.loc[mask, "status"] = (
                "success" if observations else "no_data"
            )
            status.loc[mask, "observations"] = len(observations)
            status.loc[mask, "error"] = ""

            print(f"  Recovered observations: {len(observations)}")

        except Exception as error:
            print(f"  Still failed: {error}")

        time.sleep(1)

    sort_columns = ["country_code", "indicator_code", "year"]
    data = data.sort_values(sort_columns).reset_index(drop=True)
    raw_data = raw_data.sort_values(sort_columns).reset_index(drop=True)

    data.to_csv(DATA_FILE, index=False)
    raw_data.to_csv(RAW_DATA_FILE, index=False)
    status.to_csv(STATUS_FILE, index=False)

    print("\n=== RETRY SUMMARY ===")
    print(f"Successful combinations: {(status['status'] == 'success').sum()}")
    print(f"Combinations without data: {(status['status'] == 'no_data').sum()}")
    print(f"Failed combinations remaining: {(status['status'] == 'error').sum()}")
    print(f"Total observation rows: {len(data)}")

    session.close()


if __name__ == "__main__":
    main()

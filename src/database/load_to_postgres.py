
import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import tuple_row


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "world_bank_clean.csv"

DB_HOST = os.getenv("PGHOST", "127.0.0.1")
DB_PORT = int(os.getenv("PGPORT", "5432"))
DB_NAME = os.getenv("PGDATABASE", "emerging_markets_intelligence")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASSWORD = os.getenv("PGPASSWORD")

COLUMNS = [
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

UPSERT_SQL = """
INSERT INTO economic_observations (
    country_code,
    country_name,
    indicator_code,
    indicator_name,
    business_dimension,
    year,
    value,
    unit,
    value_status
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (country_code, indicator_code, year)
DO UPDATE SET
    country_name = EXCLUDED.country_name,
    indicator_name = EXCLUDED.indicator_name,
    business_dimension = EXCLUDED.business_dimension,
    value = EXCLUDED.value,
    unit = EXCLUDED.unit,
    value_status = EXCLUDED.value_status;
"""


def main():
    if not DB_PASSWORD:
        raise SystemExit(
            "PGPASSWORD is not set. Set it in CMD before running this script."
        )

    data = pd.read_csv(DATA_FILE)

    missing_columns = sorted(set(COLUMNS) - set(data.columns))
    if missing_columns:
        raise SystemExit(f"Missing required columns: {missing_columns}")

    if data.duplicated(
        subset=["country_code", "indicator_code", "year"]
    ).any():
        raise SystemExit("Duplicate primary-key combinations found in CSV.")

    rows = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in data[COLUMNS].itertuples(index=False, name=None)
    ]

    connection_config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "connect_timeout": 10,
    }

    with psycopg.connect(**connection_config, row_factory=tuple_row) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(UPSERT_SQL, rows)

            cursor.execute("SELECT COUNT(*) FROM economic_observations;")
            total_rows = cursor.fetchone()[0]

    print("=== POSTGRESQL LOAD SUMMARY ===")
    print(f"Rows submitted: {len(rows)}")
    print(f"Rows currently in database: {total_rows}")
    
    if total_rows != len(rows):
    	raise RuntimeError(
            f"Database row count mismatch: expected {len(rows)}, "
            f"found {total_rows}"
    )
    
    print("Database row count validation passed.")
    print("UPSERT transaction committed successfully.")


if __name__ == "__main__":
    main()

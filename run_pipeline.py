
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / (
    f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

PIPELINE_STEPS = [
    (
        "Extract data from World Bank API",
        PROJECT_ROOT / "src" / "ingestion" / "fetch_all_world_bank.py",
    ),
    (
        "Validate extracted dataset",
        PROJECT_ROOT / "src" / "validation" / "validate_full_dataset.py",
    ),
    (
        "Transform dataset",
        PROJECT_ROOT / "src" / "transformation" / "transform_world_bank.py",
    ),
    (
        "Validate clean dataset",
        PROJECT_ROOT / "src" / "validation" / "validate_clean_dataset.py",
    ),
    (
        "Load data to PostgreSQL",
        PROJECT_ROOT / "src" / "database" / "load_to_postgres.py",
    ),
]


def main():
    logging.info("Pipeline started")
    logging.info("Log file: %s", log_file)

    # Check that all pipeline scripts exist before execution.
    missing_scripts = [
        str(script_path)
        for _, script_path in PIPELINE_STEPS
        if not script_path.is_file()
    ]

    if missing_scripts:
        for script in missing_scripts:
            logging.error("Required script not found: %s", script)

        logging.error("Pipeline stopped because required scripts are missing.")
        raise SystemExit(1)

    test_failure = "--test-failure" in sys.argv

    test_failure = "--test-failure" in sys.argv

    for step_name, script_path in PIPELINE_STEPS:
        logging.info("START | %s", step_name)

        try:
            if test_failure:
                # Simulate a failed process without running the actual script.
                subprocess.run(
                    [sys.executable, "-c", "raise SystemExit(1)"],
                    cwd=PROJECT_ROOT,
                    check=True,
                )
            else:
                subprocess.run(
                    [sys.executable, "-u", str(script_path)],
                    cwd=PROJECT_ROOT,
                    check=True,
                )

        except subprocess.CalledProcessError as error:
            logging.error(
                "FAILED | %s | exit code=%s",
                step_name,
                error.returncode,
            )
            logging.info("Pipeline stopped. Later steps will not run.")
            raise SystemExit(error.returncode)

        logging.info("SUCCESS | %s", step_name)

    logging.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()

# Pipeline Automation

## Current design

- **Scheduler:** Windows Task Scheduler.
- **Launcher:** `run_pipeline_scheduled.bat`.
- **Pipeline entry point:** `run_pipeline.py`.
- **Logs:** `logs/`.
- **Suggested cadence:** monthly, suitable as a starting check for annual macroeconomic series.

The launcher invokes the existing Python pipeline; it does not change extraction or transformation logic.

## Configure

1. Confirm the project path in `run_pipeline_scheduled.bat`. The supplied file assumes `%USERPROFILE%\Documents\emerging-markets-intelligence`.
2. Confirm the project virtual environment exists at `.venv` or `venv`, or that Python is available on `PATH`.
3. Ensure PostgreSQL is running and the scheduled Windows account can connect.
4. Configure `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` for the account that runs the task. Do not put a real password in the batch file or Git.
5. Run the launcher manually and inspect the latest log.
6. Confirm the run ends with `STATUS: SUCCESS`.
7. Open Task Scheduler (`taskschd.msc`) and create a monthly task that launches the batch file.
8. Run the task from Task Scheduler and inspect the new log before relying on the schedule.

## Operational considerations

- The computer must be on when the task runs.
- PostgreSQL must be available to the task account.
- The task needs access to the same Python environment and database configuration as a manual run.
- A successful execution does not guarantee that the source API has published new observations.
- Power BI Desktop does not refresh automatically just because PostgreSQL changed.

## Repeatability and duplicate prevention

The database loader checks for duplicate keys in the input and uses an upsert for `(country_code, indicator_code, year)`. Test repeat runs against a safe development database before scheduling production-like execution.

## Troubleshooting

| Symptom | Check |
|---|---|
| Script not found | Update the project path and confirm `run_pipeline.py` exists |
| Python/package error | Run with the project's virtual environment manually |
| PostgreSQL connection failure | Check service status, environment variables, and task-account permissions |
| No new observations | Review logs and source availability; annual source data may not have changed |
| Task works manually but not on schedule | Check the task's account, working directory, and environment variables |
| Power BI shows old values | Refresh the report separately after the pipeline succeeds |

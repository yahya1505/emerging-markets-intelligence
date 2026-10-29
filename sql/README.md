# SQL scripts

The SQL scripts in this directory contain exploratory indicator analysis and the country-risk scoring logic.

Before publishing or rerunning them against a new database:

1. Read the scripts and confirm execution order.
2. Confirm any required base tables and constraints exist.
3. Test scripts in a development database first.
4. Check that risk-scoring outputs match `docs/risk_scoring_methodology.md`.
5. Remove credentials and machine-specific settings from any future additions.

These scripts are not a complete database backup or a one-click schema migration.

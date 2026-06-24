# Data Pipeline

This document will describe the financial data ingestion and transformation workflow.

The planned pipeline will collect public financial data, store raw inputs, transform them into clean tables, and prepare model-ready datasets.

Current database foundation:

- PostgreSQL runs locally through Docker Compose.
- SQLAlchemy creates the first tables during backend startup.
- Seed data inserts Apple/AAPL sample records into PostgreSQL.
- API endpoints read from PostgreSQL instead of hardcoded Python mock data.
- No SEC, FRED, OpenAI, dbt, or external API calls are used yet.

Current tables:

- `companies`
- `financial_metrics`
- `model_predictions`
- `pipeline_runs`

Initial data folders:

- `data/raw/` for source files as collected.
- `data/processed/` for cleaned or transformed outputs.

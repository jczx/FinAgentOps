# FinAgentOps Backend

This folder contains the FastAPI backend foundation for FinAgentOps.

The API reads data from local PostgreSQL. The SEC ingestion script fetches public SEC company facts for the configured company universe and transforms them into yearly financial metrics.

The first database version keeps things simple: SQLAlchemy creates the tables on startup, and the seed function keeps the Apple/AAPL company row available if it does not already exist. Alembic migrations will be added later when the schema becomes more mature.

## Database Configuration

The backend reads `DATABASE_URL` from environment variables using `python-dotenv`. It checks:

1. The repository root `.env`
2. `apps/backend/.env`

If both files exist, the backend-specific file takes precedence. Both `.env` locations are ignored by Git.

### Option 1: Local Docker Compose

From the repository root, start PostgreSQL:

```powershell
docker compose up -d postgres
```

Check the container:

```powershell
docker compose ps
```

Create `.env` in the repository root:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@localhost:5432/your_database_name
SEC_USER_AGENT=Your Name your.email@domain.com
```

### Option 2: PostgreSQL in Ubuntu VMware

For PostgreSQL running in the Ubuntu VM at `192.168.136.131`, create or update the Windows repository root `.env`:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@your_vm_ip:5432/your_database_name
POSTGRES_DB=your_database_name
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_PORT=5432
SEC_USER_AGENT=Your Name your.email@domain.com
```

Confirm the VM database port is reachable from Windows:

```powershell
Test-NetConnection 192.168.136.131 -Port 5432
```

The VM IP is configuration, so it is not hardcoded in the Python application.

## Local Development

Create and activate a virtual environment from this folder:

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the backend tests:

```powershell
python -m pytest
```

The tests use a temporary SQLite database. This keeps the test suite fast and avoids requiring private PostgreSQL credentials in CI.

## SEC Company Facts Ingestion

The public-data ingestion slice supports the configured SEC company universe. It fetches SEC company facts JSON, stores the original response in `raw_sec_company_facts`, extracts selected annual facts into `financial_facts`, and updates yearly rows in `financial_metrics`.

Required environment variables:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@your_vm_ip:5432/your_database_name
SEC_USER_AGENT=Your Name your.email@domain.com
```

The SEC asks automated clients to send a descriptive `User-Agent` with contact information. Replace the placeholder with your real name/project and email before running the script.

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe scripts\ingest_sec_company.py --ticker AAPL
```

Run all configured companies:

```powershell
.\.venv\Scripts\python.exe scripts\ingest_sec_company.py --all
```

The script is idempotent: rerunning it updates the raw response, extracted facts, and yearly metric rows without duplicating yearly metrics.

Revenue may appear under different SEC concepts. The ingestion maps these SEC concept names to the normalized metric `revenue`:

- `Revenues`
- `SalesRevenueNet`
- `RevenueFromContractWithCustomerExcludingAssessedTax`

The original SEC concept name remains in `financial_facts.fact_name`, and the analytics meaning is stored in `financial_facts.normalized_metric_name`.

To verify that data was inserted, connect to PostgreSQL and run:

```sql
SELECT
	  ticker
	, cik
	, fetched_at
FROM raw_sec_company_facts
WHERE ticker = 'AAPL';

SELECT
	  ticker
	, fact_name
	, normalized_metric_name
	, fiscal_year
	, value
FROM financial_facts
WHERE ticker = 'AAPL'
ORDER BY fiscal_year DESC, fact_name;

SELECT
	  fiscal_year
	, revenue
	, net_income
	, total_assets
	, total_liabilities
	, operating_cash_flow
	, profit_margin
	, debt_to_assets_ratio
	, return_on_assets
	, operating_cash_flow_margin
	, revenue_growth
	, net_income_growth
FROM financial_metrics fm
JOIN companies c
	ON c.id = fm.company_id
WHERE c.ticker = 'AAPL'
ORDER BY fiscal_year DESC;

SELECT
	  source_name
	, status
	, started_at
	, finished_at
	, records_processed
	, error_message
FROM pipeline_runs
ORDER BY last_run_at DESC
LIMIT 5;
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

On startup, the backend creates these tables if they do not exist:

- `companies`
- `financial_metrics`
- `model_predictions`
- `pipeline_runs`
- `raw_sec_company_facts`
- `financial_facts`

It then runs an idempotent seed function. Repeated backend restarts do not create duplicate Apple/AAPL companies, and old `Demo FY` metric rows are removed in favor of real SEC-derived yearly metrics.

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

You can also test endpoints directly in the browser:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/companies
http://127.0.0.1:8000/companies/AAPL
http://127.0.0.1:8000/companies/AAPL/metrics
http://127.0.0.1:8000/companies/comparison?tickers=AAPL,MSFT,NVDA
http://127.0.0.1:8000/companies/AAPL/risk-score
http://127.0.0.1:8000/pipeline/status
```

If PostgreSQL is not running, `/health` reports the database as unreachable and data endpoints return a `503` error with a helpful message.

For local Docker Compose, stop PostgreSQL from the repository root:

```powershell
docker compose down
```

## Available Endpoints

- `GET /health`
- `GET /companies`
- `GET /companies/comparison?tickers=AAPL,MSFT,NVDA`
- `GET /companies/{ticker}`
- `GET /companies/{ticker}/metrics`
- `GET /companies/{ticker}/risk-score`
- `GET /pipeline/status`

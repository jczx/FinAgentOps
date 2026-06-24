# FinAgentOps Backend

This folder contains the initial FastAPI backend foundation for FinAgentOps.

The API reads seeded sample data from local PostgreSQL. It does not call external services such as SEC, FRED, OpenAI, or any other API.

The first database version keeps things simple: SQLAlchemy creates the tables on startup, and the seed function inserts Apple/AAPL sample data if it does not already exist. Alembic migrations will be added later when the schema becomes more mature.

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
DATABASE_URL=postgresql+psycopg2://finagentops_user:finagentops_password@localhost:5432/finagentops
```

### Option 2: PostgreSQL in Ubuntu VMware

For PostgreSQL running in the Ubuntu VM at `192.168.136.131`, create or update the Windows repository root `.env`:

```env
DATABASE_URL=postgresql+psycopg2://finagentops_user:finagentops_password@192.168.136.131:5432/finagentops
POSTGRES_DB=finagentops
POSTGRES_USER=finagentops_user
POSTGRES_PASSWORD=finagentops_password
POSTGRES_PORT=5432
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

Run the API:

```powershell
uvicorn app.main:app --reload
```

On startup, the backend creates these tables if they do not exist:

- `companies`
- `financial_metrics`
- `model_predictions`
- `pipeline_runs`

It then runs an idempotent seed function. Repeated backend restarts do not create duplicate Apple/AAPL companies or duplicate demo records.

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
- `GET /companies/{ticker}`
- `GET /companies/{ticker}/metrics`
- `GET /companies/{ticker}/risk-score`
- `GET /pipeline/status`

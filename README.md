# FinAgentOps

FinAgentOps is a portfolio project for building an AI-powered financial intelligence platform. The project is designed to demonstrate practical skills across data engineering, data science, AI engineering, and DevOps.

## Problem Statement

Financial analysis often requires collecting company filings, transforming raw data into useful metrics, modeling business performance, and explaining results clearly. These steps are usually spread across many tools and can be difficult to reproduce or automate.

FinAgentOps focuses on building a structured workflow that turns public financial data into clean datasets, model-ready features, forecasts, and AI-assisted analyst summaries.

## Solution Overview

The planned platform will combine:

- A web dashboard for exploring financial insights.
- A FastAPI backend for serving data and model outputs.
- PostgreSQL for storing structured financial data.
- Data pipelines for collecting and transforming SEC EDGAR data.
- Machine learning models for financial KPI analysis.
- Explainability tools such as SHAP to make model behavior easier to understand.
- A RAG-based AI analyst for grounded interpretation of financial information.
- DevOps practices such as Docker, GitHub Actions, and cloud deployment.

Important: this project is for education and portfolio demonstration. It should clearly separate factual data, model predictions, and AI-generated interpretation. It should not provide financial investment advice.

## Planned Tech Stack

Frontend:

- React
- TypeScript
- Vite
- SCSS

Backend:

- Python
- FastAPI
- PostgreSQL

Data and Machine Learning:

- SEC EDGAR data
- dbt
- XGBoost
- SHAP

AI:

- Retrieval-Augmented Generation, also called RAG
- LangGraph
- MCP in a later phase

DevOps:

- Docker
- GitHub Actions
- Cloud deployment in a later phase

## Roadmap Summary

1. Repository foundation
2. Frontend dashboard shell
3. FastAPI backend
4. PostgreSQL database
5. Financial data ingestion
6. KPI transformation
7. XGBoost model
8. RAG analyst
9. LangGraph agent
10. MCP tools
11. Docker and CI/CD
12. Deployment

## Local Setup

### Database

FinAgentOps uses PostgreSQL for local backend data. The first database version is intentionally simple: the backend creates tables on startup and seeds Apple/AAPL sample data if it is missing.

#### Option 1: Local Docker Compose

Start PostgreSQL from the repository root:

```powershell
docker compose up -d postgres
```

Check that the container is running:

```powershell
docker compose ps
```

Stop PostgreSQL when you are finished:

```powershell
docker compose down
```

Use this database URL in `.env`:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@localhost:5432/your_database_name
```

#### Option 2: Ubuntu VMware VM

When PostgreSQL runs in Docker inside the Ubuntu VM at `192.168.136.131`, create or update `.env` in the repository root:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@your_vm_ip:5432/your_database_name
POSTGRES_DB=your_database_name
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_PORT=5432
```

The backend reads `DATABASE_URL` at startup. The VM address belongs in `.env`, not in Python source code. Confirm connectivity from Windows before starting FastAPI:

```powershell
Test-NetConnection 192.168.136.131 -Port 5432
```

The `TcpTestSucceeded` value should be `True`.

### SEC Ingestion and Local Scheduler

SEC ingestion currently supports Apple/AAPL. The script fetches public SEC company facts, stores the untouched SEC JSON in PostgreSQL table `raw_sec_company_facts`, extracts structured accounting facts into `financial_facts`, and updates yearly metrics in `financial_metrics`. Each run is also logged in `pipeline_runs`.

Before running ingestion, the Ubuntu VM and its Docker PostgreSQL container must be running. The repo clone used by the VM is:

```text
/home/julio/FinAgentOps
```

Run ingestion manually from inside the VM:

```bash
cd /home/julio/FinAgentOps
/home/julio/FinAgentOps/.venv/bin/python scripts/ingest_sec_company.py --ticker AAPL
```

A local Linux cron job runs the same ingestion every day at `06:00` VM time. It changes into the repo directory, writes a start timestamp to `logs/sec_ingestion.log`, runs the ingestion script, appends stdout/stderr to the same log file, and writes an end timestamp if the command succeeds.

Check the local scheduler log from inside the VM:

```bash
tail -n 100 /home/julio/FinAgentOps/logs/sec_ingestion.log
```

Verify recent pipeline runs in PostgreSQL:

```sql
SELECT
	  source_name
	, status
	, started_at
	, finished_at
	, records_processed
	, error_message
FROM pipeline_runs
ORDER BY last_run_at DESC
LIMIT 10;
```

This cron setup is a local development scheduler. Later, the same ingestion workflow can be moved to a cloud scheduler such as GitHub Actions scheduled workflows, Cloud Run Jobs plus Cloud Scheduler, or another managed orchestration service.

### Run Frontend and Backend Together

The frontend reads dashboard data from the FastAPI backend. The backend reads seeded sample data from PostgreSQL. You need three running pieces: PostgreSQL, the backend API, and the Vite frontend.

First, ensure PostgreSQL is running. For local Docker Compose:

```powershell
docker compose up -d postgres
```

For VMware, start the PostgreSQL container inside Ubuntu and confirm port `5432` is reachable from Windows.

Terminal 1, start the backend from Windows:

```powershell
cd apps/backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

On startup, FastAPI creates any missing initial tables and runs the idempotent Apple/AAPL seed.

Terminal 2, start the frontend:

```powershell
cd apps/frontend
npm install
npm run dev
```

The frontend expects the backend URL from this environment variable:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

For local development, copy `apps/frontend/.env.example` to `apps/frontend/.env` if you need to customize the backend URL. Do not commit `.env`.

Open the frontend at:

```text
http://localhost:5173
```

Open the backend API docs at:

```text
http://127.0.0.1:8000/docs
```

### Frontend

The frontend dashboard shell lives in `apps/frontend/`.

To run it locally:

```bash
cd apps/frontend
npm install
npm run dev
```

Then open the local URL printed by Vite, usually:

```text
http://localhost:5173
```

To create a production build:

```bash
cd apps/frontend
npm run build
```

### Backend

The backend API foundation lives in `apps/backend/`.

To create and activate a Python virtual environment on Windows PowerShell:

```powershell
cd apps/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

To install backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

To run the local FastAPI server after PostgreSQL is running:

```powershell
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The backend loads environment variables from either the repository root `.env` or `apps/backend/.env`. A backend-specific file takes precedence when both exist.

The data ingestion pipeline, machine learning workflow, and AI agent will be added in later project phases.

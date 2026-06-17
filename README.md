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

### Run Frontend and Backend Together

The frontend now reads mock dashboard data from the FastAPI backend. You need two terminals: one terminal runs the backend API, and the other terminal runs the Vite frontend.

Terminal 1, start the backend:

```powershell
cd apps/backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

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

To run the local FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The database, data pipeline, machine learning workflow, and AI agent will be added in later project phases.

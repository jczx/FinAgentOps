# FinAgentOps Backend

This folder contains the initial FastAPI backend foundation for FinAgentOps.

The API currently uses mock data only. It does not connect to a real database and does not call external services such as SEC, FRED, OpenAI, or any other API.

## Local Development

Create and activate a virtual environment from this folder:

```powershell
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

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Available Endpoints

- `GET /health`
- `GET /companies`
- `GET /companies/{ticker}`
- `GET /companies/{ticker}/metrics`
- `GET /companies/{ticker}/risk-score`
- `GET /pipeline/status`

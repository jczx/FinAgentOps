# MCP PostgreSQL Server

FinAgentOps includes a local MCP server for read-only PostgreSQL access.

The server connects to the same database as the backend by reading `DATABASE_URL` from:

1. `apps/backend/.env`
2. repository root `.env`

Do not put credentials in MCP config files. Keep secrets in `.env`, which is ignored by Git.

## What It Does

The MCP server exposes safe database tools for agents and MCP clients:

- `list_tables`
- `describe_table`
- `run_readonly_query`
- `get_company_metrics`
- `get_latest_pipeline_runs`

`run_readonly_query` accepts only one `SELECT` or `WITH` query. It blocks write and DDL keywords such as `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, and `TRUNCATE`.

This is intentionally read-only. It is meant for inspection, debugging, and analysis, not for modifying project data.

## Install Dependencies

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r apps\backend\requirements.txt
```

From the Ubuntu VM:

```bash
cd /home/julio/FinAgentOps
/home/julio/FinAgentOps/.venv/bin/python -m pip install -r apps/backend/requirements.txt
```

## Start The Server Manually

From Windows:

```powershell
.\.venv\Scripts\python.exe scripts\mcp_postgres_server.py
```

From the Ubuntu VM:

```bash
cd /home/julio/FinAgentOps
/home/julio/FinAgentOps/.venv/bin/python scripts/mcp_postgres_server.py
```

The process runs as an MCP stdio server. It is normally launched by an MCP client rather than used directly in a terminal.

## MCP Client Configuration

Use the Windows configuration when the MCP client runs on Windows and can reach the VM PostgreSQL port through `DATABASE_URL`.

```json
{
	"mcpServers": {
		"finagentops-postgres": {
			"command": "C:\\Users\\JulioCaesar\\FinAgentOps\\.venv\\Scripts\\python.exe",
			"args": [
				"C:\\Users\\JulioCaesar\\FinAgentOps\\scripts\\mcp_postgres_server.py"
			],
			"cwd": "C:\\Users\\JulioCaesar\\FinAgentOps"
		}
	}
}
```

Use the Ubuntu configuration when the MCP client runs inside the VM.

```json
{
	"mcpServers": {
		"finagentops-postgres": {
			"command": "/home/julio/FinAgentOps/.venv/bin/python",
			"args": [
				"/home/julio/FinAgentOps/scripts/mcp_postgres_server.py"
			],
			"cwd": "/home/julio/FinAgentOps"
		}
	}
}
```

## Database Requirements

The PostgreSQL Docker container in the Ubuntu VM must be running.

From Windows, confirm the VM database port is reachable:

```powershell
Test-NetConnection 192.168.136.131 -Port 5432
```

From the Ubuntu VM, confirm the container is running:

```bash
docker ps
```

## Example Read-Only Queries

```sql
SELECT
	  com.ticker
	, COUNT( met.id )        AS metric_rows
	, MAX( met.fiscal_year ) AS latest_year
FROM
	public.companies  com
LEFT JOIN
	public.financial_metrics  met
	ON com.id = met.company_id
GROUP BY
	  com.ticker
ORDER BY
	  com.ticker
;
```

```sql
SELECT
	  run.source_name
	, run.status
	, run.finished_at
	, run.records_processed
FROM
	public.pipeline_runs  run
ORDER BY
	  run.finished_at DESC
LIMIT 10
;
```

## Safety Notes

- Keep `.env` out of Git.
- Use a database user with the minimum privileges needed.
- This server blocks write SQL at the application layer, but database permissions are still the strongest safety boundary.
- For production, create a dedicated read-only PostgreSQL role for MCP access.

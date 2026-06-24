import os
import re
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, RowMapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "apps" / "backend"

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(REPOSITORY_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
	print(
		"DATABASE_URL is required. Set it in .env before starting the MCP server.",
		file=sys.stderr,
	)
	raise SystemExit(1)

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	connect_args={"connect_timeout": 5},
)
mcp = FastMCP("FinAgentOps PostgreSQL")

ALLOWED_SCHEMAS = {"public"}
BLOCKED_SQL_PATTERNS = re.compile(
	r"\b("
	r"alter|analyze|call|comment|copy|create|delete|drop|execute|grant|insert|"
	r"listen|lock|merge|notify|reindex|reset|revoke|set|truncate|update|vacuum"
	r")\b",
	re.IGNORECASE,
)


def serialize_value(value: Any) -> Any:
	if isinstance(value, datetime | date):
		return value.isoformat()

	if isinstance(value, Decimal):
		return float(value)

	return value


def serialize_row(row: RowMapping) -> dict[str, Any]:
	return {key: serialize_value(value) for key, value in row.items()}


def validate_table_name(table_name: str) -> str:
	if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", table_name):
		raise ValueError("Table name must contain only letters, numbers, and underscores.")

	return table_name


def validate_readonly_sql(sql: str) -> str:
	clean_sql = sql.strip().rstrip(";")
	lower_sql = clean_sql.lower()

	if ";" in clean_sql:
		raise ValueError("Only one SQL statement is allowed.")

	if not lower_sql.startswith(("select", "with")):
		raise ValueError("Only read-only SELECT or WITH queries are allowed.")

	if BLOCKED_SQL_PATTERNS.search(clean_sql):
		raise ValueError("This MCP server allows read-only queries only.")

	return clean_sql


def clamp_limit(limit: int) -> int:
	return max(1, min(limit, 500))


def fetch_rows(sql: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
	with engine.connect() as connection:
		result = connection.execute(text(sql), parameters or {})
		return [serialize_row(row) for row in result.mappings().all()]


@mcp.tool()
def list_tables() -> list[dict[str, str]]:
	"""List available PostgreSQL tables in the public schema."""
	inspector = inspect(engine)
	return [
		{"schema": "public", "table_name": table_name}
		for table_name in inspector.get_table_names(schema="public")
	]


@mcp.tool()
def describe_table(table_name: str) -> list[dict[str, Any]]:
	"""Describe columns for a table in the public schema."""
	valid_table_name = validate_table_name(table_name)
	inspector = inspect(engine)

	if valid_table_name not in inspector.get_table_names(schema="public"):
		raise ValueError(f"Table '{valid_table_name}' was not found in public schema.")

	return [
		{
			"column_name": column["name"],
			"data_type": str(column["type"]),
			"nullable": bool(column["nullable"]),
		}
		for column in inspector.get_columns(valid_table_name, schema="public")
	]


@mcp.tool()
def run_readonly_query(sql: str, limit: int = 100) -> list[dict[str, Any]]:
	"""Run a read-only SELECT/WITH query and return at most 500 rows."""
	clean_sql = validate_readonly_sql(sql)
	row_limit = clamp_limit(limit)
	wrapped_sql = f"SELECT * FROM ({clean_sql}) AS mcp_query LIMIT :row_limit"
	return fetch_rows(wrapped_sql, {"row_limit": row_limit})


@mcp.tool()
def get_company_metrics(ticker: str, limit: int = 10) -> list[dict[str, Any]]:
	"""Return yearly financial metrics for a ticker, newest fiscal years first."""
	row_limit = clamp_limit(limit)
	return fetch_rows(
		"""
		SELECT
			  com.ticker
			, com.name AS company_name
			, met.fiscal_year
			, met.fiscal_period
			, met.revenue
			, met.net_income
			, met.total_assets
			, met.total_liabilities
			, met.operating_cash_flow
			, met.profit_margin
			, met.debt_to_assets_ratio
			, met.return_on_assets
			, met.operating_cash_flow_margin
			, met.revenue_growth
			, met.net_income_growth
			, met.created_at
			, met.updated_at
		FROM
			public.financial_metrics  met
		INNER JOIN
			public.companies  com
			ON com.id = met.company_id
		WHERE
			com.ticker = :ticker
		ORDER BY
			  met.fiscal_year DESC
		LIMIT :row_limit
		""",
		{"ticker": ticker.upper(), "row_limit": row_limit},
	)


@mcp.tool()
def get_latest_pipeline_runs(limit: int = 10) -> list[dict[str, Any]]:
	"""Return latest pipeline run records."""
	row_limit = clamp_limit(limit)
	return fetch_rows(
		"""
		SELECT
			  run.source_name
			, run.status
			, run.started_at
			, run.finished_at
			, run.records_processed
			, run.error_message
			, run.message
		FROM
			public.pipeline_runs  run
		ORDER BY
			  run.last_run_at DESC
		LIMIT :row_limit
		""",
		{"row_limit": row_limit},
	)


if __name__ == "__main__":
	mcp.run()

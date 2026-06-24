from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select


def test_health_returns_reachable_database(client: TestClient) -> None:
	response = client.get("/health")

	assert response.status_code == 200
	assert response.json() == {
		"status": "ok",
		"service": "finagentops-api",
		"database": "reachable",
	}


def test_companies_returns_seeded_company_from_database(client: TestClient) -> None:
	response = client.get("/companies")

	assert response.status_code == 200
	companies = response.json()
	assert len(companies) == 1
	assert companies[0]["ticker"] == "AAPL"
	assert companies[0]["name"] == "Apple Inc."


def test_company_detail_returns_database_record(client: TestClient) -> None:
	response = client.get("/companies/AAPL")

	assert response.status_code == 200
	assert response.json() == {
		"name": "Apple Inc.",
		"ticker": "AAPL",
		"exchange": "NASDAQ",
		"sector": "Technology",
	}


def test_company_metrics_returns_yearly_rows_sorted_by_fiscal_year(
	client: TestClient,
) -> None:
	from app.database import SessionLocal
	from app.db_models import CompanyRecord, FinancialMetricRecord

	with SessionLocal() as db:
		company = db.scalar(select(CompanyRecord).where(CompanyRecord.ticker == "AAPL"))
		assert company is not None
		db.add_all(
			[
				FinancialMetricRecord(
					company_id=company.id,
					fiscal_year=2023,
					fiscal_period="FY 2023",
					revenue=120,
					net_income=30,
					total_assets=200,
					total_liabilities=80,
					operating_cash_flow=40,
					revenue_growth=20.0,
					net_income_growth=50.0,
					profit_margin=25.0,
					debt_to_assets=40.0,
					debt_to_assets_ratio=40.0,
					return_on_assets=15.0,
					operating_cash_flow_margin=33.33,
					free_cash_flow_margin=33.33,
					created_at=datetime(2026, 6, 25, 8, 0, 0),
					updated_at=datetime(2026, 6, 25, 9, 0, 0),
				),
				FinancialMetricRecord(
					company_id=company.id,
					fiscal_year=2022,
					fiscal_period="FY 2022",
					revenue=100,
					net_income=20,
					total_assets=180,
					total_liabilities=70,
					operating_cash_flow=35,
					revenue_growth=0.0,
					net_income_growth=0.0,
					profit_margin=20.0,
					debt_to_assets=38.89,
					debt_to_assets_ratio=38.89,
					return_on_assets=11.11,
					operating_cash_flow_margin=35.0,
					free_cash_flow_margin=35.0,
					created_at=datetime(2026, 6, 25, 8, 0, 0),
					updated_at=datetime(2026, 6, 25, 9, 0, 0),
				),
			]
		)
		db.commit()

	response = client.get("/companies/AAPL/metrics")

	assert response.status_code == 200
	body = response.json()
	assert body["ticker"] == "AAPL"
	assert body["company_name"] == "Apple Inc."
	assert [row["fiscal_year"] for row in body["yearly_metrics"]] == [2022, 2023]
	assert body["yearly_metrics"][-1]["revenue"] == 120
	assert body["yearly_metrics"][-1]["created_at"] == "2026-06-25T08:00:00"
	assert body["metrics"][0]["label"] == "Revenue"
	assert body["metrics"][0]["value"] == 120.0


def test_pipeline_status_returns_latest_runs(client: TestClient) -> None:
	from app.database import SessionLocal
	from app.db_models import PipelineRunRecord

	with SessionLocal() as db:
		db.add(
			PipelineRunRecord(
				source_name="sec_companyfacts_aapl",
				status="SUCCESS",
				started_at=datetime(2026, 6, 25, 6, 0, 0),
				finished_at=datetime(2026, 6, 25, 6, 1, 0),
				last_run_at=datetime(2026, 6, 25, 6, 1, 0),
				records_processed=42,
				steps_completed=4,
				total_steps=4,
				message="SEC ingestion completed.",
				error_message="",
			)
		)
		db.commit()

	response = client.get("/pipeline/status")

	assert response.status_code == 200
	body = response.json()
	assert body["status"] == "SUCCESS"
	assert body["runs"][0]["source_name"] == "sec_companyfacts_aapl"
	assert body["runs"][0]["records_processed"] == 42

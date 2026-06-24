from sqlalchemy import select


def test_safe_percentage_handles_zero_and_missing_denominators(client) -> None:
	from app.services.sec_ingestion import safe_percentage, safe_percentage_change

	assert safe_percentage(10, 0) == 0.0
	assert safe_percentage(None, 100) == 0.0
	assert safe_percentage(25, 100) == 25.0
	assert safe_percentage_change(120, 100) == 20.0
	assert safe_percentage_change(120, 0) == 0.0


def test_extract_annual_facts_maps_multiple_revenue_concepts(client) -> None:
	from app.services.sec_ingestion import extract_annual_facts

	payload = {
		"facts": {
			"us-gaap": {
				"SalesRevenueNet": {
					"units": {
						"USD": [
							{
								"form": "10-K",
								"fp": "FY",
								"fy": 2023,
								"val": 120,
								"filed": "2024-01-01",
								"accn": "sales-revenue",
							}
						]
					}
				},
				"RevenueFromContractWithCustomerExcludingAssessedTax": {
					"units": {
						"USD": [
							{
								"form": "10-K",
								"fp": "FY",
								"fy": 2024,
								"val": 140,
								"filed": "2025-01-01",
								"accn": "contract-revenue",
							}
						]
					}
				},
			}
		}
	}

	facts = extract_annual_facts(payload)

	assert {fact["fact_name"] for fact in facts} == {
		"SalesRevenueNet",
		"RevenueFromContractWithCustomerExcludingAssessedTax",
	}
	assert all(fact["normalized_metric_name"] == "revenue" for fact in facts)


def test_update_financial_metrics_is_idempotent(client) -> None:
	from app.database import SessionLocal
	from app.db_models import CompanyRecord, FinancialFactRecord, FinancialMetricRecord
	from app.services.sec_ingestion import update_financial_metrics

	with SessionLocal() as db:
		company = db.scalar(select(CompanyRecord).where(CompanyRecord.ticker == "AAPL"))
		assert company is not None
		db.add_all(
			[
				FinancialFactRecord(
					company_id=company.id,
					ticker="AAPL",
					fact_name="Revenues",
					normalized_metric_name="revenue",
					fiscal_year=2023,
					fiscal_period="FY",
					form="10-K",
					unit="USD",
					value=100,
				),
				FinancialFactRecord(
					company_id=company.id,
					ticker="AAPL",
					fact_name="NetIncomeLoss",
					normalized_metric_name="net_income",
					fiscal_year=2023,
					fiscal_period="FY",
					form="10-K",
					unit="USD",
					value=25,
				),
				FinancialFactRecord(
					company_id=company.id,
					ticker="AAPL",
					fact_name="Assets",
					normalized_metric_name="total_assets",
					fiscal_year=2023,
					fiscal_period="FY",
					form="10-K",
					unit="USD",
					value=200,
				),
				FinancialFactRecord(
					company_id=company.id,
					ticker="AAPL",
					fact_name="Liabilities",
					normalized_metric_name="total_liabilities",
					fiscal_year=2023,
					fiscal_period="FY",
					form="10-K",
					unit="USD",
					value=80,
				),
			]
		)
		db.commit()

		update_financial_metrics(db, company)
		update_financial_metrics(db, company)
		db.commit()

		metrics = db.scalars(
			select(FinancialMetricRecord).where(
				FinancialMetricRecord.company_id == company.id,
				FinancialMetricRecord.fiscal_period == "FY 2023",
			)
		).all()

	assert len(metrics) == 1
	assert metrics[0].revenue == 100
	assert metrics[0].profit_margin == 25.0
	assert metrics[0].debt_to_assets_ratio == 40.0

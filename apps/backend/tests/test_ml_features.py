from sqlalchemy import select


def test_build_ml_feature_rows_creates_next_year_target(client) -> None:
	from app.database import SessionLocal
	from app.db_models import CompanyRecord, FinancialMetricRecord
	from app.services.ml_features import build_ml_feature_rows

	with SessionLocal() as db:
		company = db.scalar(select(CompanyRecord).where(CompanyRecord.ticker == "AAPL"))
		assert company is not None
		db.add_all(
			[
				FinancialMetricRecord(
					company_id=company.id,
					fiscal_year=2022,
					fiscal_period="FY 2022",
					revenue=100,
					net_income=25,
					total_assets=200,
					total_liabilities=80,
					operating_cash_flow=35,
					revenue_growth=10.0,
					net_income_growth=20.0,
					profit_margin=25.0,
					debt_to_assets=40.0,
					debt_to_assets_ratio=40.0,
					return_on_assets=12.5,
					operating_cash_flow_margin=35.0,
					free_cash_flow_margin=35.0,
				),
				FinancialMetricRecord(
					company_id=company.id,
					fiscal_year=2023,
					fiscal_period="FY 2023",
					revenue=90,
					net_income=20,
					total_assets=210,
					total_liabilities=100,
					operating_cash_flow=30,
					revenue_growth=-10.0,
					net_income_growth=-20.0,
					profit_margin=22.22,
					debt_to_assets=47.62,
					debt_to_assets_ratio=47.62,
					return_on_assets=9.52,
					operating_cash_flow_margin=33.33,
					free_cash_flow_margin=33.33,
				),
			],
		)
		db.commit()

		rows = build_ml_feature_rows(db)

	aapl_2022 = next(row for row in rows if row.ticker == "AAPL" and row.fiscal_year == 2022)
	aapl_2023 = next(row for row in rows if row.ticker == "AAPL" and row.fiscal_year == 2023)

	assert aapl_2022.target_next_year_deterioration == 1
	assert aapl_2023.target_next_year_deterioration is None

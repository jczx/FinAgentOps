def test_calculate_financial_health_score_returns_explainable_components(
	client,
) -> None:
	from app.db_models import FinancialMetricRecord
	from app.services.financial_health import calculate_financial_health_score

	metric = FinancialMetricRecord(
		company_id=1,
		fiscal_year=2023,
		fiscal_period="FY 2023",
		revenue=100,
		net_income=25,
		revenue_growth=20.0,
		net_income_growth=10.0,
		profit_margin=25.0,
		debt_to_assets=40.0,
		debt_to_assets_ratio=40.0,
		return_on_assets=12.0,
		operating_cash_flow_margin=30.0,
		free_cash_flow_margin=30.0,
	)

	health_score = calculate_financial_health_score(metric)

	assert health_score.score == 81.4
	assert health_score.grade == "B"
	assert [component.name for component in health_score.components] == [
		"growth",
		"profitability",
		"leverage",
		"cash_flow",
	]

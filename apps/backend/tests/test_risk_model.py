from pathlib import Path

from app.services.ml_features import MLFeatureRow


def make_row(year: int, target: int | None) -> MLFeatureRow:
	return MLFeatureRow(
		ticker="AAPL",
		company_name="Apple Inc.",
		fiscal_year=year,
		revenue=100 + year,
		net_income=20 + year,
		total_assets=200 + year,
		total_liabilities=80 + year,
		operating_cash_flow=30 + year,
		revenue_growth=5.0 if target == 0 else -5.0,
		net_income_growth=4.0 if target == 0 else -4.0,
		profit_margin=20.0 if target == 0 else 10.0,
		debt_to_assets_ratio=35.0 if target == 0 else 70.0,
		return_on_assets=12.0 if target == 0 else 4.0,
		operating_cash_flow_margin=30.0 if target == 0 else 8.0,
		target_next_year_deterioration=target,
	)


def test_train_risk_model_writes_model_and_metadata(tmp_path: Path) -> None:
	from app.services.risk_model import train_risk_model

	rows = [make_row(2000 + index, index % 2) for index in range(24)]

	result = train_risk_model(rows, tmp_path)

	assert result.model_path.exists()
	assert result.metadata_path.exists()
	assert result.training_rows > 0
	assert result.test_rows > 0
	assert result.accuracy is not None

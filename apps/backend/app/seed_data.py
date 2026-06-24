from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import (
	CompanyRecord,
	FinancialMetricRecord,
	ModelPredictionRecord,
	PipelineRunRecord,
)


def seed_database(db: Session) -> None:
	apple = db.scalar(
		select(CompanyRecord).where(CompanyRecord.ticker == "AAPL"),
	)

	if apple is None:
		apple = CompanyRecord(
			ticker="AAPL",
			name="Apple Inc.",
			exchange="NASDAQ",
			sector="Technology",
		)
		db.add(apple)
		db.flush()

	demo_metrics = db.scalars(
		select(FinancialMetricRecord).where(
			FinancialMetricRecord.company_id == apple.id,
			FinancialMetricRecord.fiscal_period == "Demo FY",
		),
	).all()

	for metric in demo_metrics:
		db.delete(metric)

	existing_prediction = db.scalar(
		select(ModelPredictionRecord).where(
			ModelPredictionRecord.company_id == apple.id,
		),
	)

	if existing_prediction is None:
		db.add(
			ModelPredictionRecord(
				company_id=apple.id,
				risk_score="Low",
				summary=(
					"Demo analysis indicates stable profitability, strong cash flow, "
					"and manageable leverage."
				),
				factors="Positive free cash flow|Healthy margins|Moderate debt load",
			),
		)

	existing_pipeline_run = db.scalar(
		select(PipelineRunRecord).where(
			PipelineRunRecord.source_name == "demo_financial_seed",
		),
	)

	if existing_pipeline_run is None:
		db.add(
			PipelineRunRecord(
				source_name="demo_financial_seed",
				status="Success",
				records_processed=1,
				last_run_at=datetime.now(timezone.utc).replace(tzinfo=None),
				steps_completed=4,
				total_steps=4,
				message=(
					"PostgreSQL demo data loaded successfully. "
					"No external data was fetched."
				),
			),
		)

	db.commit()

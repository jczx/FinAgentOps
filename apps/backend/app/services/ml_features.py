import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import CompanyRecord, FinancialMetricRecord


@dataclass(frozen=True)
class MLFeatureRow:
	ticker: str
	company_name: str
	fiscal_year: int
	revenue: int | None
	net_income: int | None
	total_assets: int | None
	total_liabilities: int | None
	operating_cash_flow: int | None
	revenue_growth: float | None
	net_income_growth: float | None
	profit_margin: float | None
	debt_to_assets_ratio: float | None
	return_on_assets: float | None
	operating_cash_flow_margin: float | None
	target_next_year_deterioration: int | None


def deterioration_signal_count(
	current: FinancialMetricRecord,
	next_metric: FinancialMetricRecord,
) -> int:
	signals = [
		next_metric.revenue is not None
		and current.revenue is not None
		and next_metric.revenue < current.revenue,
		next_metric.net_income is not None
		and current.net_income is not None
		and next_metric.net_income < current.net_income,
		next_metric.profit_margin < current.profit_margin,
		(
			next_metric.debt_to_assets_ratio is not None
			and current.debt_to_assets_ratio is not None
			and next_metric.debt_to_assets_ratio > current.debt_to_assets_ratio
		),
		(
			next_metric.operating_cash_flow is not None
			and current.operating_cash_flow is not None
			and next_metric.operating_cash_flow < current.operating_cash_flow
		),
	]

	return sum(1 for signal in signals if signal)


def deterioration_target(
	current: FinancialMetricRecord,
	next_metric: FinancialMetricRecord | None,
) -> int | None:
	if next_metric is None:
		return None

	return 1 if deterioration_signal_count(current, next_metric) >= 2 else 0


def build_ml_feature_rows(db: Session) -> list[MLFeatureRow]:
	companies = db.scalars(select(CompanyRecord).order_by(CompanyRecord.ticker)).all()
	rows: list[MLFeatureRow] = []

	for company in companies:
		metrics = db.scalars(
			select(FinancialMetricRecord)
			.where(FinancialMetricRecord.company_id == company.id)
			.where(FinancialMetricRecord.fiscal_period != "Demo FY")
			.where(FinancialMetricRecord.fiscal_year.is_not(None))
			.order_by(FinancialMetricRecord.fiscal_year),
		).all()
		metrics_by_year = {
			metric.fiscal_year: metric
			for metric in metrics
			if metric.fiscal_year is not None
		}

		for metric in metrics:
			if metric.fiscal_year is None:
				continue

			next_metric = metrics_by_year.get(metric.fiscal_year + 1)
			rows.append(
				MLFeatureRow(
					ticker=company.ticker,
					company_name=company.name,
					fiscal_year=metric.fiscal_year,
					revenue=metric.revenue,
					net_income=metric.net_income,
					total_assets=metric.total_assets,
					total_liabilities=metric.total_liabilities,
					operating_cash_flow=metric.operating_cash_flow,
					revenue_growth=metric.revenue_growth,
					net_income_growth=metric.net_income_growth,
					profit_margin=metric.profit_margin,
					debt_to_assets_ratio=metric.debt_to_assets_ratio,
					return_on_assets=metric.return_on_assets,
					operating_cash_flow_margin=metric.operating_cash_flow_margin,
					target_next_year_deterioration=deterioration_target(
						metric,
						next_metric,
					),
				),
			)

	return rows


def write_ml_feature_csv(rows: list[MLFeatureRow], output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)

	with output_path.open("w", newline="", encoding="utf-8") as output_file:
		writer = csv.DictWriter(
			output_file,
			fieldnames=list(MLFeatureRow.__dataclass_fields__.keys()),
		)
		writer.writeheader()
		for row in rows:
			writer.writerow(asdict(row))

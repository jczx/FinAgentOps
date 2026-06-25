from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import (
	CompanyRecord,
	FinancialMetricRecord,
)
from app.models import (
	Company,
	CompanyComparisonItem,
	CompanyComparisonResponse,
	CompanyMetricsResponse,
	FinancialHealthScoreResponse,
	HealthScoreComponent,
	Metric,
	RiskScoreResponse,
	YearlyFinancialMetric,
)
from app.services.financial_health import calculate_financial_health_score
from app.services.risk_model import predict_risk_from_metric

router = APIRouter(prefix="/companies", tags=["companies"])
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MODEL_PATH = REPOSITORY_ROOT / "models" / "risk_model.joblib"
MODEL_METADATA_PATH = REPOSITORY_ROOT / "models" / "risk_model_metadata.json"


def normalize_ticker(ticker: str) -> str:
	return ticker.strip().upper()


def database_unavailable_error() -> HTTPException:
	return HTTPException(
		status_code=503,
		detail=(
			"Database is not reachable. Check that PostgreSQL is running, verify "
			"network access, and confirm DATABASE_URL."
		),
	)


def company_response(company: CompanyRecord) -> Company:
	return Company(
		name=company.name,
		ticker=company.ticker,
		exchange=company.exchange,
		sector=company.sector,
	)


def optional_datetime_iso(value: object) -> str | None:
	if value is None:
		return None

	if hasattr(value, "isoformat"):
		return value.isoformat()

	return str(value)


def safe_float(value: float | None) -> float:
	return 0.0 if value is None else value


def yearly_metric_response(
	company: CompanyRecord,
	row: FinancialMetricRecord,
) -> YearlyFinancialMetric:
	return YearlyFinancialMetric(
		ticker=company.ticker,
		company_name=company.name,
		fiscal_year=row.fiscal_year,
		fiscal_period=row.fiscal_period,
		revenue=row.revenue,
		net_income=row.net_income,
		total_assets=row.total_assets,
		total_liabilities=row.total_liabilities,
		operating_cash_flow=row.operating_cash_flow,
		profit_margin=safe_float(row.profit_margin),
		debt_to_assets_ratio=row.debt_to_assets_ratio,
		return_on_assets=row.return_on_assets,
		operating_cash_flow_margin=row.operating_cash_flow_margin,
		revenue_growth=safe_float(row.revenue_growth),
		net_income_growth=row.net_income_growth,
		created_at=optional_datetime_iso(getattr(row, "created_at", None)),
		updated_at=optional_datetime_iso(getattr(row, "updated_at", None)),
	)


def get_company_record_or_404(ticker: str, db: Session) -> CompanyRecord:
	normalized_ticker = normalize_ticker(ticker)

	try:
		company = db.scalar(
			select(CompanyRecord).where(CompanyRecord.ticker == normalized_ticker),
		)
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	if company is None:
		raise HTTPException(
			status_code=404,
			detail=f"Company with ticker '{normalized_ticker}' was not found.",
		)

	return company


@router.get("", response_model=list[Company])
def list_companies(db: Session = Depends(get_db)) -> list[Company]:
	try:
		companies = db.scalars(select(CompanyRecord).order_by(CompanyRecord.ticker)).all()
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	return [company_response(company) for company in companies]


@router.get("/comparison", response_model=CompanyComparisonResponse)
def compare_companies(
	tickers: str = Query(
		...,
		description="Comma-separated ticker list, for example AAPL,MSFT,NVDA.",
	),
	db: Session = Depends(get_db),
) -> CompanyComparisonResponse:
	requested_tickers = []
	for ticker in tickers.split(","):
		normalized_ticker = normalize_ticker(ticker)
		if normalized_ticker and normalized_ticker not in requested_tickers:
			requested_tickers.append(normalized_ticker)

	if not requested_tickers:
		raise HTTPException(
			status_code=400,
			detail="Provide at least one ticker, for example ?tickers=AAPL,MSFT.",
		)

	if len(requested_tickers) > 5:
		raise HTTPException(
			status_code=400,
			detail="Compare up to 5 companies at a time.",
		)

	try:
		companies = db.scalars(
			select(CompanyRecord)
			.where(CompanyRecord.ticker.in_(requested_tickers))
			.order_by(CompanyRecord.ticker),
		).all()
		company_by_ticker = {company.ticker: company for company in companies}
		metric_records = db.scalars(
			select(FinancialMetricRecord)
			.join(CompanyRecord)
			.where(CompanyRecord.ticker.in_(requested_tickers))
			.where(FinancialMetricRecord.fiscal_period != "Demo FY")
			.where(FinancialMetricRecord.fiscal_year.is_not(None))
			.order_by(CompanyRecord.ticker, FinancialMetricRecord.fiscal_year),
		).all()
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	metrics_by_ticker: dict[str, list[FinancialMetricRecord]] = {
		ticker: [] for ticker in requested_tickers
	}
	for metric_record in metric_records:
		metrics_by_ticker.setdefault(metric_record.company.ticker, []).append(
			metric_record,
		)

	comparison_items = []
	for ticker in requested_tickers:
		company = company_by_ticker.get(ticker)
		if company is None:
			continue

		yearly_metrics = [
			yearly_metric_response(company, row)
			for row in metrics_by_ticker.get(ticker, [])
		]
		comparison_items.append(
			CompanyComparisonItem(
				ticker=company.ticker,
				company_name=company.name,
				latest_metric=yearly_metrics[-1] if yearly_metrics else None,
				yearly_metrics=yearly_metrics,
			),
		)

	return CompanyComparisonResponse(
		requested_tickers=requested_tickers,
		missing_tickers=[
			ticker for ticker in requested_tickers if ticker not in company_by_ticker
		],
		companies=comparison_items,
	)


@router.get("/{ticker}", response_model=Company)
def get_company(ticker: str, db: Session = Depends(get_db)) -> Company:
	company = get_company_record_or_404(ticker, db)
	return company_response(company)


@router.get("/{ticker}/metrics", response_model=CompanyMetricsResponse)
def get_company_metrics(
	ticker: str,
	db: Session = Depends(get_db),
) -> CompanyMetricsResponse:
	company = get_company_record_or_404(ticker, db)

	try:
		metric_records = db.scalars(
			select(FinancialMetricRecord)
			.where(FinancialMetricRecord.company_id == company.id)
			.where(FinancialMetricRecord.fiscal_period != "Demo FY")
			.where(FinancialMetricRecord.fiscal_year.is_not(None))
			.order_by(FinancialMetricRecord.fiscal_year),
		).all()
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	if not metric_records:
		return CompanyMetricsResponse(
			ticker=company.ticker,
			company_name=company.name,
			metrics=[],
			yearly_metrics=[],
		)

	metric_record = metric_records[-1]
	metrics = [
		Metric(
			label="Revenue",
			value=float(metric_record.revenue or 0),
			unit="usd",
			description=f"Total revenue for {metric_record.fiscal_period}.",
		),
		Metric(
			label="Net income",
			value=float(metric_record.net_income or 0),
			unit="usd",
			description=f"Net income for {metric_record.fiscal_period}.",
		),
		Metric(
			label="Revenue growth",
			value=safe_float(metric_record.revenue_growth),
			unit="percent",
			description="Year-over-year top-line growth.",
		),
		Metric(
			label="Profit margin",
			value=safe_float(metric_record.profit_margin),
			unit="percent",
			description="Net income as a share of revenue.",
		),
		Metric(
			label="Debt-to-assets",
			value=(
				metric_record.debt_to_assets_ratio
				if metric_record.debt_to_assets_ratio is not None
				else safe_float(metric_record.debt_to_assets)
			),
			unit="percent",
			description="Debt compared with total assets.",
		),
		Metric(
			label="Return on assets",
			value=metric_record.return_on_assets or 0.0,
			unit="percent",
			description="Net income as a share of total assets.",
		),
		Metric(
			label="Operating cash flow margin",
			value=(
				metric_record.operating_cash_flow_margin
				if metric_record.operating_cash_flow_margin is not None
				else metric_record.free_cash_flow_margin
			),
			unit="percent",
			description="Operating cash flow as a share of revenue.",
		),
	]

	return CompanyMetricsResponse(
		ticker=company.ticker,
		company_name=company.name,
		metrics=metrics,
		yearly_metrics=[yearly_metric_response(company, row) for row in metric_records],
	)


@router.get("/{ticker}/health-score", response_model=FinancialHealthScoreResponse)
def get_company_health_score(
	ticker: str,
	db: Session = Depends(get_db),
) -> FinancialHealthScoreResponse:
	company = get_company_record_or_404(ticker, db)

	try:
		metric_record = db.scalar(
			select(FinancialMetricRecord)
			.where(FinancialMetricRecord.company_id == company.id)
			.where(FinancialMetricRecord.fiscal_period != "Demo FY")
			.where(FinancialMetricRecord.fiscal_year.is_not(None))
			.order_by(desc(FinancialMetricRecord.fiscal_year)),
		)
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	if metric_record is None:
		raise HTTPException(
			status_code=404,
			detail=(
				f"No yearly metrics were found for ticker '{company.ticker}'. "
				"Run SEC ingestion first, then try again."
			),
		)

	health_score = calculate_financial_health_score(metric_record)

	return FinancialHealthScoreResponse(
		ticker=company.ticker,
		company_name=company.name,
		fiscal_year=metric_record.fiscal_year,
		fiscal_period=metric_record.fiscal_period,
		score=health_score.score,
		grade=health_score.grade,
		summary=health_score.summary,
		components=[
			HealthScoreComponent(
				name=component.name,
				score=round(component.score, 1),
				explanation=component.explanation,
			)
			for component in health_score.components
		],
	)


@router.get("/{ticker}/risk-score", response_model=RiskScoreResponse)
def get_company_risk_score(
	ticker: str,
	db: Session = Depends(get_db),
) -> RiskScoreResponse:
	company = get_company_record_or_404(ticker, db)

	try:
		metric_record = db.scalar(
			select(FinancialMetricRecord)
			.where(FinancialMetricRecord.company_id == company.id)
			.where(FinancialMetricRecord.fiscal_period != "Demo FY")
			.where(FinancialMetricRecord.fiscal_year.is_not(None))
			.order_by(desc(FinancialMetricRecord.fiscal_year)),
		)
	except SQLAlchemyError as error:
		raise database_unavailable_error() from error

	if metric_record is None:
		raise HTTPException(
			status_code=404,
			detail=(
				f"No yearly metrics were found for ticker '{company.ticker}'. "
				"Run SEC ingestion first, then train the model."
			),
		)

	try:
		prediction = predict_risk_from_metric(
			metric=metric_record,
			model_path=MODEL_PATH,
			metadata_path=MODEL_METADATA_PATH,
		)
	except FileNotFoundError as error:
		raise HTTPException(
			status_code=404,
			detail=(
				"Risk model artifact was not found. Run "
				"`python scripts/train_risk_model.py` first."
			),
		) from error

	return RiskScoreResponse(
		ticker=company.ticker,
		company_name=company.name,
		fiscal_year=metric_record.fiscal_year,
		risk_probability=prediction.probability,
		risk_label=prediction.label,
		risk_score=prediction.label,
		model_type=prediction.model_type,
		summary=prediction.summary,
		feature_columns=prediction.feature_columns,
		factors=[
			"Baseline Random Forest model trained from yearly financial metrics.",
			"Prediction estimates next-year financial deterioration risk.",
			"This is an educational model, not investment advice.",
		],
	)

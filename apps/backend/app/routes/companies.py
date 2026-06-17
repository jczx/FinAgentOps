from fastapi import APIRouter, HTTPException

from app.mock_data import MOCK_COMPANIES, MOCK_METRICS, MOCK_RISK_SCORES
from app.models import Company, CompanyMetricsResponse, RiskScoreResponse

router = APIRouter(prefix="/companies", tags=["companies"])


def normalize_ticker(ticker: str) -> str:
	return ticker.strip().upper()


def get_company_or_404(ticker: str) -> Company:
	normalized_ticker = normalize_ticker(ticker)
	company = MOCK_COMPANIES.get(normalized_ticker)

	if company is None:
		raise HTTPException(
			status_code=404,
			detail=f"Company with ticker '{normalized_ticker}' was not found.",
		)

	return company


@router.get("", response_model=list[Company])
def list_companies() -> list[Company]:
	return list(MOCK_COMPANIES.values())


@router.get("/{ticker}", response_model=Company)
def get_company(ticker: str) -> Company:
	return get_company_or_404(ticker)


@router.get("/{ticker}/metrics", response_model=CompanyMetricsResponse)
def get_company_metrics(ticker: str) -> CompanyMetricsResponse:
	company = get_company_or_404(ticker)
	metrics = MOCK_METRICS.get(company.ticker, [])

	return CompanyMetricsResponse(ticker=company.ticker, metrics=metrics)


@router.get("/{ticker}/risk-score", response_model=RiskScoreResponse)
def get_company_risk_score(ticker: str) -> RiskScoreResponse:
	company = get_company_or_404(ticker)
	risk_score = MOCK_RISK_SCORES.get(company.ticker)

	if risk_score is None:
		raise HTTPException(
			status_code=404,
			detail=f"Risk score for ticker '{company.ticker}' was not found.",
		)

	return risk_score

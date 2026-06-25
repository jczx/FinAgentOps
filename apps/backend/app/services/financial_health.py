from dataclasses import dataclass

from app.db_models import FinancialMetricRecord


@dataclass(frozen=True)
class HealthScoreComponent:
	name: str
	score: float
	explanation: str


@dataclass(frozen=True)
class FinancialHealthScore:
	score: float
	grade: str
	summary: str
	components: list[HealthScoreComponent]


def clamp_score(value: float) -> float:
	return max(0.0, min(100.0, value))


def score_growth(metric: FinancialMetricRecord) -> HealthScoreComponent:
	revenue_growth = metric.revenue_growth or 0.0
	net_income_growth = metric.net_income_growth or 0.0
	score = 50.0 + revenue_growth * 1.5 + net_income_growth * 0.75

	return HealthScoreComponent(
		name="growth",
		score=clamp_score(score),
		explanation=(
			"Growth compares year-over-year revenue growth and net income growth. "
			f"Latest values: revenue growth {revenue_growth:.1f}%, "
			f"net income growth {net_income_growth:.1f}%."
		),
	)


def score_profitability(metric: FinancialMetricRecord) -> HealthScoreComponent:
	profit_margin = metric.profit_margin or 0.0
	return_on_assets = metric.return_on_assets or 0.0
	score = 35.0 + profit_margin * 1.4 + return_on_assets * 1.2

	return HealthScoreComponent(
		name="profitability",
		score=clamp_score(score),
		explanation=(
			"Profitability combines profit margin and return on assets. "
			f"Latest values: profit margin {profit_margin:.1f}%, "
			f"return on assets {return_on_assets:.1f}%."
		),
	)


def score_leverage(metric: FinancialMetricRecord) -> HealthScoreComponent:
	debt_ratio = (
		metric.debt_to_assets_ratio
		if metric.debt_to_assets_ratio is not None
		else metric.debt_to_assets
	)
	debt_ratio = debt_ratio or 0.0
	score = 100.0 - debt_ratio

	return HealthScoreComponent(
		name="leverage",
		score=clamp_score(score),
		explanation=(
			"Leverage rewards companies with a lower liabilities-to-assets ratio. "
			f"Latest debt-to-assets ratio: {debt_ratio:.1f}%."
		),
	)


def score_cash_flow(metric: FinancialMetricRecord) -> HealthScoreComponent:
	cash_flow_margin = (
		metric.operating_cash_flow_margin
		if metric.operating_cash_flow_margin is not None
		else metric.free_cash_flow_margin
	)
	cash_flow_margin = cash_flow_margin or 0.0
	score = 35.0 + cash_flow_margin * 1.8

	return HealthScoreComponent(
		name="cash_flow",
		score=clamp_score(score),
		explanation=(
			"Cash flow quality uses operating cash flow margin when available. "
			f"Latest cash flow margin: {cash_flow_margin:.1f}%."
		),
	)


def grade_for_score(score: float) -> str:
	if score >= 85:
		return "A"
	if score >= 70:
		return "B"
	if score >= 55:
		return "C"
	if score >= 40:
		return "D"

	return "F"


def summary_for_grade(grade: str) -> str:
	if grade == "A":
		return "Very strong financial health based on the latest available metrics."
	if grade == "B":
		return "Solid financial health with generally favorable metric signals."
	if grade == "C":
		return "Mixed financial health; some areas look stable while others need review."
	if grade == "D":
		return "Weak financial health signals; review trend and leverage carefully."

	return "Very weak financial health signals based on the available metrics."


def calculate_financial_health_score(
	metric: FinancialMetricRecord,
) -> FinancialHealthScore:
	components = [
		score_growth(metric),
		score_profitability(metric),
		score_leverage(metric),
		score_cash_flow(metric),
	]
	weights = {
		"growth": 0.25,
		"profitability": 0.30,
		"leverage": 0.20,
		"cash_flow": 0.25,
	}
	overall_score = sum(
		component.score * weights[component.name] for component in components
	)
	overall_score = round(clamp_score(overall_score), 1)
	grade = grade_for_score(overall_score)

	return FinancialHealthScore(
		score=overall_score,
		grade=grade,
		summary=summary_for_grade(grade),
		components=components,
	)

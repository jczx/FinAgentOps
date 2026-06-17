from app.models import Company, Metric, PipelineStatusResponse, RiskScoreResponse


MOCK_COMPANIES: dict[str, Company] = {
	"AAPL": Company(
		name="Apple Inc.",
		ticker="AAPL",
		exchange="NASDAQ",
		sector="Technology",
	),
}

MOCK_METRICS: dict[str, list[Metric]] = {
	"AAPL": [
		Metric(
			label="Revenue growth",
			value=8.2,
			unit="percent",
			description="Year-over-year top-line growth.",
		),
		Metric(
			label="Profit margin",
			value=22.5,
			unit="percent",
			description="Net income as a share of revenue.",
		),
		Metric(
			label="Debt-to-assets",
			value=31.4,
			unit="percent",
			description="Debt compared with total assets.",
		),
		Metric(
			label="Free cash flow margin",
			value=18.7,
			unit="percent",
			description="Free cash flow as a share of revenue.",
		),
	],
}

MOCK_RISK_SCORES: dict[str, RiskScoreResponse] = {
	"AAPL": RiskScoreResponse(
		ticker="AAPL",
		risk_score="Low",
		summary=(
			"Mock analysis indicates stable profitability, strong cash flow, "
			"and manageable leverage."
		),
		factors=["Positive free cash flow", "Healthy margins", "Moderate debt load"],
	),
}

MOCK_PIPELINE_STATUS = PipelineStatusResponse(
	status="Success",
	last_run="Mock run",
	steps_completed=4,
	total_steps=4,
	message="Mock pipeline completed successfully. No external data was fetched.",
)

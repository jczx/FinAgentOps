from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
	status: str = Field(examples=["ok"])
	service: str = Field(examples=["finagentops-api"])
	database: str = Field(examples=["reachable"])


class Company(BaseModel):
	name: str
	ticker: str
	exchange: str
	sector: str


class Metric(BaseModel):
	label: str
	value: float
	unit: str
	description: str


class YearlyFinancialMetric(BaseModel):
	ticker: str
	company_name: str
	fiscal_year: int | None
	fiscal_period: str
	revenue: int | None
	net_income: int | None
	total_assets: int | None
	total_liabilities: int | None
	operating_cash_flow: int | None
	profit_margin: float
	debt_to_assets_ratio: float | None
	return_on_assets: float | None
	operating_cash_flow_margin: float | None
	revenue_growth: float
	net_income_growth: float | None
	created_at: str | None = None
	updated_at: str | None = None


class CompanyMetricsResponse(BaseModel):
	ticker: str
	company_name: str
	metrics: list[Metric]
	yearly_metrics: list[YearlyFinancialMetric] = Field(default_factory=list)


class RiskScoreResponse(BaseModel):
	ticker: str
	risk_score: str
	summary: str
	factors: list[str]


class PipelineRun(BaseModel):
	source_name: str
	status: str
	started_at: str | None
	finished_at: str | None
	records_processed: int
	error_message: str
	message: str


class PipelineStatusResponse(BaseModel):
	status: str
	last_run: str
	steps_completed: int
	total_steps: int
	message: str
	runs: list[PipelineRun] = Field(default_factory=list)

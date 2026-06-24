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


class CompanyMetricsResponse(BaseModel):
	ticker: str
	metrics: list[Metric]


class RiskScoreResponse(BaseModel):
	ticker: str
	risk_score: str
	summary: str
	factors: list[str]


class PipelineStatusResponse(BaseModel):
	status: str
	last_run: str
	steps_completed: int
	total_steps: int
	message: str

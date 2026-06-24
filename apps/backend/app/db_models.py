from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CompanyRecord(Base):
	__tablename__ = "companies"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
	name: Mapped[str] = mapped_column(String(255))
	exchange: Mapped[str] = mapped_column(String(64))
	sector: Mapped[str] = mapped_column(String(128))

	metrics: Mapped[list["FinancialMetricRecord"]] = relationship(
		back_populates="company",
		cascade="all, delete-orphan",
	)
	predictions: Mapped[list["ModelPredictionRecord"]] = relationship(
		back_populates="company",
		cascade="all, delete-orphan",
	)
	facts: Mapped[list["FinancialFactRecord"]] = relationship(
		back_populates="company",
		cascade="all, delete-orphan",
	)


class FinancialMetricRecord(Base):
	__tablename__ = "financial_metrics"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
	fiscal_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
	fiscal_period: Mapped[str] = mapped_column(String(32))
	revenue: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	net_income: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	total_assets: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	total_liabilities: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	operating_cash_flow: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	revenue_growth: Mapped[float] = mapped_column(Float)
	net_income_growth: Mapped[float | None] = mapped_column(Float, nullable=True)
	profit_margin: Mapped[float] = mapped_column(Float)
	debt_to_assets: Mapped[float] = mapped_column(Float)
	debt_to_assets_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
	return_on_assets: Mapped[float | None] = mapped_column(Float, nullable=True)
	operating_cash_flow_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
	free_cash_flow_margin: Mapped[float] = mapped_column(Float)

	company: Mapped[CompanyRecord] = relationship(back_populates="metrics")


class ModelPredictionRecord(Base):
	__tablename__ = "model_predictions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
	risk_score: Mapped[str] = mapped_column(String(32))
	summary: Mapped[str] = mapped_column(Text)
	factors: Mapped[str] = mapped_column(Text, default="")

	company: Mapped[CompanyRecord] = relationship(back_populates="predictions")


class RawSecCompanyFactsRecord(Base):
	__tablename__ = "raw_sec_company_facts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
	cik: Mapped[str] = mapped_column(String(16), index=True)
	company_name: Mapped[str] = mapped_column(String(255))
	response_json: Mapped[dict] = mapped_column(JSON)
	fetched_at: Mapped[datetime] = mapped_column(DateTime)


class FinancialFactRecord(Base):
	__tablename__ = "financial_facts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
	ticker: Mapped[str] = mapped_column(String(16), index=True)
	fact_name: Mapped[str] = mapped_column(String(128), index=True)
	normalized_metric_name: Mapped[str] = mapped_column(String(64), index=True, default="")
	fiscal_year: Mapped[int] = mapped_column(Integer, index=True)
	fiscal_period: Mapped[str] = mapped_column(String(16))
	form: Mapped[str] = mapped_column(String(16))
	unit: Mapped[str] = mapped_column(String(32))
	value: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	filed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	accession_number: Mapped[str] = mapped_column(String(32), default="")
	frame: Mapped[str] = mapped_column(String(32), default="")

	company: Mapped[CompanyRecord] = relationship(back_populates="facts")


class PipelineRunRecord(Base):
	__tablename__ = "pipeline_runs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	source_name: Mapped[str] = mapped_column(String(128))
	status: Mapped[str] = mapped_column(String(32))
	records_processed: Mapped[int] = mapped_column(Integer)
	started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	error_message: Mapped[str] = mapped_column(Text, default="")
	last_run_at: Mapped[datetime] = mapped_column(DateTime)
	steps_completed: Mapped[int] = mapped_column(Integer, default=0)
	total_steps: Mapped[int] = mapped_column(Integer, default=0)
	message: Mapped[str] = mapped_column(Text, default="")

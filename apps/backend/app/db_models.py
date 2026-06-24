from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
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


class FinancialMetricRecord(Base):
	__tablename__ = "financial_metrics"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
	fiscal_period: Mapped[str] = mapped_column(String(32))
	revenue_growth: Mapped[float] = mapped_column(Float)
	profit_margin: Mapped[float] = mapped_column(Float)
	debt_to_assets: Mapped[float] = mapped_column(Float)
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


class PipelineRunRecord(Base):
	__tablename__ = "pipeline_runs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	source_name: Mapped[str] = mapped_column(String(128))
	status: Mapped[str] = mapped_column(String(32))
	records_processed: Mapped[int] = mapped_column(Integer)
	last_run_at: Mapped[datetime] = mapped_column(DateTime)
	steps_completed: Mapped[int] = mapped_column(Integer, default=0)
	total_steps: Mapped[int] = mapped_column(Integer, default=0)
	message: Mapped[str] = mapped_column(Text, default="")

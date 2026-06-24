import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.data.company_universe import CompanyMetadata, get_company_metadata
from app.database import Base
from app.db_models import (
	CompanyRecord,
	FinancialFactRecord,
	FinancialMetricRecord,
	PipelineRunRecord,
	RawSecCompanyFactsRecord,
)

SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
IMPORTANT_FACTS = (
	"Revenues",
	"SalesRevenueNet",
	"RevenueFromContractWithCustomerExcludingAssessedTax",
	"NetIncomeLoss",
	"Assets",
	"Liabilities",
	"NetCashProvidedByUsedInOperatingActivities",
)
NORMALIZED_FACT_NAMES = {
	"Revenues": "revenue",
	"SalesRevenueNet": "revenue",
	"RevenueFromContractWithCustomerExcludingAssessedTax": "revenue",
	"NetIncomeLoss": "net_income",
	"Assets": "total_assets",
	"Liabilities": "total_liabilities",
	"NetCashProvidedByUsedInOperatingActivities": "operating_cash_flow",
}
NORMALIZED_FACT_PRIORITY = {
	"Revenues": 1,
	"SalesRevenueNet": 2,
	"RevenueFromContractWithCustomerExcludingAssessedTax": 3,
	"NetIncomeLoss": 1,
	"Assets": 1,
	"Liabilities": 1,
	"NetCashProvidedByUsedInOperatingActivities": 1,
}


def run_sec_company_ingestion(ticker: str, db: Session, engine: Engine) -> int:
	company_metadata = get_company_metadata(ticker)

	ensure_ingestion_schema(engine)

	started_at = utc_now()
	pipeline_run = PipelineRunRecord(
		source_name=f"sec_companyfacts_{company_metadata.ticker.lower()}",
		status="RUNNING",
		started_at=started_at,
		finished_at=None,
		last_run_at=started_at,
		records_processed=0,
		steps_completed=0,
		total_steps=4,
		message="SEC company facts ingestion started.",
		error_message="",
	)
	db.add(pipeline_run)
	db.commit()
	db.refresh(pipeline_run)

	try:
		payload = fetch_company_facts(company_metadata.cik)
		company = upsert_company(db, company_metadata, payload)
		remove_demo_financial_metrics(db, company)
		upsert_raw_company_facts(db, company_metadata, payload)
		facts_processed = upsert_financial_facts(
			db,
			company,
			company_metadata.ticker,
			payload,
		)
		backfill_normalized_fact_names(db)
		update_financial_metrics(db, company)

		finished_at = utc_now()
		pipeline_run.status = "SUCCESS"
		pipeline_run.records_processed = facts_processed
		pipeline_run.steps_completed = 4
		pipeline_run.finished_at = finished_at
		pipeline_run.last_run_at = finished_at
		pipeline_run.message = "SEC company facts ingestion completed successfully."
		db.commit()

		return facts_processed
	except Exception as error:
		db.rollback()
		finished_at = utc_now()
		pipeline_run.status = "FAILED"
		pipeline_run.finished_at = finished_at
		pipeline_run.last_run_at = finished_at
		pipeline_run.error_message = str(error)
		pipeline_run.message = "SEC company facts ingestion failed."
		db.add(pipeline_run)
		db.commit()
		raise


def ensure_ingestion_schema(engine: Engine) -> None:
	Base.metadata.create_all(bind=engine)

	ensure_missing_columns(
		engine=engine,
		table_name="pipeline_runs",
		missing_columns={
			"started_at": "TIMESTAMP",
			"finished_at": "TIMESTAMP",
			"error_message": "TEXT DEFAULT ''",
		},
	)
	ensure_missing_columns(
		engine=engine,
		table_name="financial_facts",
		missing_columns={
			"normalized_metric_name": "VARCHAR(64) DEFAULT ''",
		},
	)
	ensure_missing_columns(
		engine=engine,
		table_name="financial_metrics",
		missing_columns={
			"fiscal_year": "INTEGER",
			"revenue": "BIGINT",
			"net_income": "BIGINT",
			"total_assets": "BIGINT",
			"total_liabilities": "BIGINT",
			"operating_cash_flow": "BIGINT",
			"net_income_growth": "DOUBLE PRECISION",
			"debt_to_assets_ratio": "DOUBLE PRECISION",
			"return_on_assets": "DOUBLE PRECISION",
			"operating_cash_flow_margin": "DOUBLE PRECISION",
			"created_at": "TIMESTAMP",
			"updated_at": "TIMESTAMP",
		},
	)


def ensure_missing_columns(
	engine: Engine,
	table_name: str,
	missing_columns: dict[str, str],
) -> None:
	columns = {column["name"] for column in inspect(engine).get_columns(table_name)}

	with engine.begin() as connection:
		for column_name, column_type in missing_columns.items():
			if column_name not in columns:
				connection.execute(
					text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"),
				)


def remove_demo_financial_metrics(db: Session, company: CompanyRecord) -> None:
	demo_metrics = db.scalars(
		select(FinancialMetricRecord).where(
			FinancialMetricRecord.company_id == company.id,
			FinancialMetricRecord.fiscal_period == "Demo FY",
		),
	).all()

	for metric in demo_metrics:
		db.delete(metric)


def backfill_normalized_fact_names(db: Session) -> None:
	fact_rows = db.scalars(select(FinancialFactRecord)).all()

	for row in fact_rows:
		normalized_name = NORMALIZED_FACT_NAMES.get(row.fact_name)
		if normalized_name:
			row.normalized_metric_name = normalized_name


def fetch_company_facts(cik: str) -> dict[str, Any]:
	user_agent = os.getenv("SEC_USER_AGENT", "").strip()
	if not user_agent or "example.com" in user_agent:
		raise ValueError(
			"SEC_USER_AGENT must be set to a real contact value, for example "
			"'Your Name your.email@domain.com'."
		)

	request = Request(
		SEC_COMPANY_FACTS_URL.format(cik=cik),
		headers={
			"Accept": "application/json",
			"User-Agent": user_agent,
		},
	)

	try:
		with urlopen(request, timeout=30) as response:
			return json.loads(response.read().decode("utf-8"))
	except HTTPError as error:
		raise RuntimeError(f"SEC request failed with status {error.code}.") from error
	except URLError as error:
		raise RuntimeError(f"SEC request failed: {error.reason}.") from error


def upsert_company(
	db: Session,
	company_metadata: CompanyMetadata,
	payload: dict[str, Any],
) -> CompanyRecord:
	company = db.scalar(
		select(CompanyRecord).where(
			CompanyRecord.ticker == company_metadata.ticker,
		),
	)
	if company is None:
		company = CompanyRecord(
			ticker=company_metadata.ticker,
			name=payload.get("entityName", company_metadata.name),
			exchange=company_metadata.exchange,
			sector=company_metadata.sector,
		)
		db.add(company)
		db.flush()
	else:
		company.name = payload.get("entityName", company_metadata.name)
		company.exchange = company_metadata.exchange
		company.sector = company_metadata.sector

	return company


def upsert_raw_company_facts(
	db: Session,
	company_metadata: CompanyMetadata,
	payload: dict[str, Any],
) -> None:
	raw_record = db.scalar(
		select(RawSecCompanyFactsRecord).where(
			RawSecCompanyFactsRecord.ticker == company_metadata.ticker,
		),
	)

	if raw_record is None:
		raw_record = RawSecCompanyFactsRecord(
			ticker=company_metadata.ticker,
			cik=company_metadata.cik,
			company_name=payload.get("entityName", company_metadata.name),
			response_json=payload,
			fetched_at=utc_now(),
		)
		db.add(raw_record)
	else:
		raw_record.cik = company_metadata.cik
		raw_record.company_name = payload.get("entityName", company_metadata.name)
		raw_record.response_json = payload
		raw_record.fetched_at = utc_now()


def upsert_financial_facts(
	db: Session,
	company: CompanyRecord,
	ticker: str,
	payload: dict[str, Any],
) -> int:
	annual_facts = extract_annual_facts(payload)
	records_processed = 0

	for fact in annual_facts:
		record = db.scalar(
			select(FinancialFactRecord).where(
				FinancialFactRecord.company_id == company.id,
				FinancialFactRecord.fact_name == fact["fact_name"],
				FinancialFactRecord.fiscal_year == fact["fiscal_year"],
				FinancialFactRecord.fiscal_period == fact["fiscal_period"],
			),
		)

		if record is None:
			record = FinancialFactRecord(company_id=company.id, ticker=ticker, **fact)
			db.add(record)
		else:
			record.ticker = ticker
			record.normalized_metric_name = fact["normalized_metric_name"]
			record.form = fact["form"]
			record.unit = fact["unit"]
			record.value = fact["value"]
			record.filed_at = fact["filed_at"]
			record.accession_number = fact["accession_number"]
			record.frame = fact["frame"]

		records_processed += 1

	db.flush()
	return records_processed


def extract_annual_facts(payload: dict[str, Any]) -> list[dict[str, Any]]:
	us_gaap_facts = payload.get("facts", {}).get("us-gaap", {})
	extracted_facts: list[dict[str, Any]] = []

	for fact_name in IMPORTANT_FACTS:
		fact_payload = us_gaap_facts.get(fact_name)
		if not fact_payload:
			continue

		units = fact_payload.get("units", {})
		unit_name = "USD" if "USD" in units else next(iter(units), "")
		if not unit_name:
			continue

		latest_by_year: dict[int, dict[str, Any]] = {}
		for fact_row in units.get(unit_name, []):
			if fact_row.get("form") != "10-K" or fact_row.get("fp") != "FY":
				continue

			fiscal_year = fact_row.get("fy")
			value = fact_row.get("val")
			if fiscal_year is None or value is None:
				continue

			current = latest_by_year.get(int(fiscal_year))
			if current is None or fact_row.get("filed", "") > current.get("filed", ""):
				latest_by_year[int(fiscal_year)] = fact_row

		for fiscal_year, fact_row in sorted(latest_by_year.items()):
			extracted_facts.append(
				{
					"fact_name": fact_name,
					"normalized_metric_name": NORMALIZED_FACT_NAMES[fact_name],
					"fiscal_year": fiscal_year,
					"fiscal_period": "FY",
					"form": fact_row.get("form", ""),
					"unit": unit_name,
					"value": int(fact_row["val"]),
					"filed_at": parse_sec_date(fact_row.get("filed")),
					"accession_number": fact_row.get("accn", ""),
					"frame": fact_row.get("frame", ""),
				}
			)

	return extracted_facts


def update_financial_metrics(db: Session, company: CompanyRecord) -> None:
	fact_rows = db.scalars(
		select(FinancialFactRecord)
		.where(FinancialFactRecord.company_id == company.id)
		.order_by(FinancialFactRecord.fiscal_year),
	).all()
	facts_by_year: dict[int, dict[str, FinancialFactRecord]] = {}

	for row in fact_rows:
		if row.value is None or not row.normalized_metric_name:
			continue

		year_facts = facts_by_year.setdefault(row.fiscal_year, {})
		current = year_facts.get(row.normalized_metric_name)
		if should_replace_fact(current, row):
			year_facts[row.normalized_metric_name] = row

	for fiscal_year, facts in sorted(facts_by_year.items()):
		revenue = fact_value(facts, "revenue")
		if revenue is None:
			continue

		previous_facts = facts_by_year.get(fiscal_year - 1, {})
		previous_revenue = fact_value(previous_facts, "revenue")
		net_income = fact_value(facts, "net_income")
		previous_net_income = fact_value(previous_facts, "net_income")
		total_assets = fact_value(facts, "total_assets")
		total_liabilities = fact_value(facts, "total_liabilities")
		operating_cash_flow = fact_value(facts, "operating_cash_flow")

		fiscal_period = f"FY {fiscal_year}"
		metric = db.scalar(
			select(FinancialMetricRecord).where(
				FinancialMetricRecord.company_id == company.id,
				FinancialMetricRecord.fiscal_period == fiscal_period,
			),
		)
		processed_at = utc_now()

		values = {
			"fiscal_year": fiscal_year,
			"revenue": revenue,
			"net_income": net_income,
			"total_assets": total_assets,
			"total_liabilities": total_liabilities,
			"operating_cash_flow": operating_cash_flow,
			"revenue_growth": safe_percentage_change(revenue, previous_revenue),
			"net_income_growth": safe_percentage_change(net_income, previous_net_income),
			"profit_margin": safe_percentage(net_income, revenue),
			"debt_to_assets": safe_percentage(total_liabilities, total_assets),
			"debt_to_assets_ratio": safe_percentage(total_liabilities, total_assets),
			"return_on_assets": safe_percentage(net_income, total_assets),
			"operating_cash_flow_margin": safe_percentage(operating_cash_flow, revenue),
			"free_cash_flow_margin": safe_percentage(operating_cash_flow, revenue),
			"updated_at": processed_at,
		}

		if metric is None:
			db.add(
				FinancialMetricRecord(
					company_id=company.id,
					fiscal_period=fiscal_period,
					created_at=processed_at,
					**values,
				),
			)
		else:
			if metric.created_at is None:
				metric.created_at = processed_at
			for field_name, value in values.items():
				setattr(metric, field_name, value)


def should_replace_fact(
	current: FinancialFactRecord | None,
	candidate: FinancialFactRecord,
) -> bool:
	if current is None:
		return True

	current_priority = NORMALIZED_FACT_PRIORITY.get(current.fact_name, 99)
	candidate_priority = NORMALIZED_FACT_PRIORITY.get(candidate.fact_name, 99)
	if candidate_priority != current_priority:
		return candidate_priority < current_priority

	current_filed_at = current.filed_at or datetime.min
	candidate_filed_at = candidate.filed_at or datetime.min
	return candidate_filed_at > current_filed_at


def fact_value(
	facts: dict[str, FinancialFactRecord],
	normalized_metric_name: str,
) -> int | None:
	row = facts.get(normalized_metric_name)
	if row is None:
		return None

	return row.value


def safe_percentage(numerator: int | None, denominator: int | None) -> float:
	if numerator is None or denominator in (None, 0):
		return 0.0

	return round((numerator / denominator) * 100, 2)


def safe_percentage_change(current: int | None, previous: int | None) -> float:
	if current is None or previous in (None, 0):
		return 0.0

	return round(((current - previous) / previous) * 100, 2)


def parse_sec_date(value: str | None) -> datetime | None:
	if not value:
		return None

	return datetime.strptime(value, "%Y-%m-%d")


def utc_now() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)

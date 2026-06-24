# Data Pipeline

This document describes the financial data ingestion and transformation workflow.

The planned pipeline will collect public financial data, store raw inputs, transform them into clean tables, and prepare model-ready datasets.

Current database foundation:

- PostgreSQL runs locally through Docker Compose.
- SQLAlchemy creates the first tables during backend startup.
- Seed data keeps the Apple/AAPL company row available in PostgreSQL.
- API endpoints read from PostgreSQL instead of hardcoded Python mock data.
- The first SEC ingestion script can fetch Apple/AAPL company facts from the public SEC API.
- No FRED, OpenAI, dbt, scheduler, Airflow, or agent workflow is used yet.

Current tables:

- `companies`
- `financial_metrics`
- `model_predictions`
- `pipeline_runs`
- `raw_sec_company_facts`
- `financial_facts`

Initial data folders:

- `data/raw/` for source files as collected.
- `data/processed/` for cleaned or transformed outputs.

## SEC Company Facts Ingestion

The current ingestion script supports only AAPL. This narrow scope keeps the foundation understandable before expanding to multiple companies.

Source endpoint:

```text
https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
```

Required environment variables:

```env
DATABASE_URL=postgresql+psycopg2://finagentops_user:finagentops_password@192.168.136.131:5432/finagentops
SEC_USER_AGENT=Your Name your.email@domain.com
```

`SEC_USER_AGENT` should identify the project and include a real contact email. The SEC uses this to contact automated clients if there is a traffic or access issue.

Run from the repository root:

```powershell
python scripts/ingest_sec_company.py --ticker AAPL
```

The script performs four steps:

1. Fetch the public SEC company facts JSON.
2. Store the untouched response in `raw_sec_company_facts`.
3. Extract annual `10-K` facts into `financial_facts`.
4. Update or insert AAPL yearly rows in `financial_metrics`.

Extracted facts:

- `Revenues`
- `SalesRevenueNet`
- `RevenueFromContractWithCustomerExcludingAssessedTax`
- `NetIncomeLoss`
- `Assets`
- `Liabilities`
- `NetCashProvidedByUsedInOperatingActivities`

Revenue is intentionally mapped from several SEC concepts because companies can report the same business idea under different XBRL tags across years. `financial_facts.fact_name` keeps the original SEC concept name, while `financial_facts.normalized_metric_name` stores the analytics-friendly name such as `revenue`, `net_income`, or `operating_cash_flow`.

`financial_metrics` stores both actual yearly financial numbers and derived ratios:

- `fiscal_year`
- `fiscal_period`
- `revenue`
- `net_income`
- `total_assets`
- `total_liabilities`
- `operating_cash_flow`
- `profit_margin`
- `debt_to_assets_ratio`
- `return_on_assets`
- `operating_cash_flow_margin`
- `revenue_growth`
- `net_income_growth`

The older `free_cash_flow_margin` column is kept for compatibility, but it currently mirrors operating cash flow margin until capital expenditure extraction is added.

## Verification Queries

After running the ingestion, connect to PostgreSQL and verify the raw payload:

```sql
SELECT
	  ticker
	, cik
	, fetched_at
FROM raw_sec_company_facts
WHERE ticker = 'AAPL';
```

Verify extracted facts:

```sql
SELECT
	  ticker
	, fact_name
	, normalized_metric_name
	, fiscal_year
	, value
FROM financial_facts
WHERE ticker = 'AAPL'
ORDER BY fiscal_year DESC, fact_name;
```

Verify that revenue is populated from all supported SEC revenue concepts:

```sql
SELECT
	  fact_name
	, normalized_metric_name
	, COUNT(*) AS row_count
	, MIN(fiscal_year) AS first_year
	, MAX(fiscal_year) AS latest_year
FROM financial_facts
WHERE ticker = 'AAPL'
	AND normalized_metric_name = 'revenue'
GROUP BY fact_name, normalized_metric_name
ORDER BY first_year;
```

Verify transformed yearly metrics:

```sql
SELECT
	  fm.fiscal_year
	, fm.revenue
	, fm.net_income
	, fm.total_assets
	, fm.total_liabilities
	, fm.operating_cash_flow
	, fm.profit_margin
	, fm.debt_to_assets_ratio
	, fm.return_on_assets
	, fm.operating_cash_flow_margin
	, fm.revenue_growth
	, fm.net_income_growth
FROM financial_metrics fm
JOIN companies c
	ON c.id = fm.company_id
WHERE c.ticker = 'AAPL'
ORDER BY fm.fiscal_year DESC;
```

Check that old demo rows are gone:

```sql
SELECT
	  fm.fiscal_period
	, COUNT(*) AS row_count
FROM financial_metrics fm
JOIN companies c
	ON c.id = fm.company_id
WHERE c.ticker = 'AAPL'
	AND fm.fiscal_period = 'Demo FY'
GROUP BY fm.fiscal_period;
```

Verify pipeline logging:

```sql
SELECT
	  source_name
	, status
	, started_at
	, finished_at
	, records_processed
	, error_message
FROM pipeline_runs
ORDER BY last_run_at DESC
LIMIT 5;
```

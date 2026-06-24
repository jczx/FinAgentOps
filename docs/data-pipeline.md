# Data Pipeline

This document describes the financial data ingestion and transformation workflow.

The planned pipeline will collect public financial data, store raw inputs, transform them into clean tables, and prepare model-ready datasets.

Current database foundation:

- PostgreSQL runs locally through Docker Compose.
- SQLAlchemy creates the first tables during backend startup.
- Seed data keeps the Apple/AAPL company row available in PostgreSQL.
- API endpoints read from PostgreSQL instead of hardcoded Python mock data.
- The SEC ingestion script can fetch company facts for the configured public-company universe.
- A local Linux cron job in the Ubuntu VM runs SEC ingestion for the full configured company universe daily.
- No FRED, OpenAI, dbt, Airflow, or agent workflow is used yet.

Current tables:

- `companies`
- `financial_metrics`
- `model_predictions`
- `pipeline_runs`
- `raw_sec_company_facts`
- `financial_facts`

## Dashboard API Usage

The dashboard now uses real multi-company PostgreSQL data instead of hardcoded company options.

Backend endpoints used by the frontend:

```text
GET /companies
GET /companies/{ticker}
GET /companies/{ticker}/metrics
GET /pipeline/status
```

`GET /companies/{ticker}/metrics` returns yearly rows from `financial_metrics`, sorted by fiscal year. Each yearly metric includes the company ticker, company name, fiscal year, fiscal period, actual financial values, ratio KPIs, growth KPIs, `created_at`, and `updated_at`. Missing numeric values are returned as `null` where the database has no value, and the frontend displays available data without crashing.

`financial_metrics.created_at` records when a yearly metric row was first created by ingestion. `financial_metrics.updated_at` records the most recent ingestion transformation time for that row. These PostgreSQL `TIMESTAMP` values are stored as Berlin-local time using the `Europe/Berlin` timezone. After deploying this schema change, rerun `scripts/ingest_sec_company.py --all` once so existing rows receive timestamp values.

`GET /pipeline/status` returns the latest pipeline summary plus the latest pipeline runs so the dashboard can show operational ingestion status.

Initial data folders:

- `data/raw/` for source files as collected.
- `data/processed/` for cleaned or transformed outputs.

## SEC Company Facts Ingestion

The current ingestion script supports this 15-company large-cap SEC filer universe:

| Ticker | CIK | Company |
| --- | --- | --- |
| `AAPL` | `0000320193` | Apple Inc. |
| `MSFT` | `0000789019` | Microsoft Corporation |
| `GOOGL` | `0001652044` | Alphabet Inc. |
| `AMZN` | `0001018724` | Amazon.com Inc. |
| `NVDA` | `0001045810` | NVIDIA Corporation |
| `META` | `0001326801` | Meta Platforms Inc. |
| `AVGO` | `0001730168` | Broadcom Inc. |
| `TSLA` | `0001318605` | Tesla Inc. |
| `BRK.B` | `0001067983` | Berkshire Hathaway Inc. |
| `LLY` | `0000059478` | Eli Lilly and Company |
| `JPM` | `0000019617` | JPMorgan Chase & Co. |
| `WMT` | `0000104169` | Walmart Inc. |
| `V` | `0001403161` | Visa Inc. |
| `ORCL` | `0001341439` | Oracle Corporation |
| `MA` | `0001141391` | Mastercard Incorporated |

The mapping lives in `apps/backend/app/data/company_universe.py`.

Source endpoint pattern:

```text
https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
```

Required environment variables:

```env
DATABASE_URL=postgresql+psycopg2://your_postgres_user:your_postgres_password@your_vm_ip:5432/your_database_name
SEC_USER_AGENT=Your Name your.email@domain.com
```

`SEC_USER_AGENT` should identify the project and include a real contact email. The SEC uses this to contact automated clients if there is a traffic or access issue.

Before running ingestion, the Ubuntu VM and the Docker PostgreSQL container inside the VM must be running. The script needs database access through `DATABASE_URL`, and the SEC request needs `SEC_USER_AGENT`.

Run manually from the repository root on Windows:

```powershell
python scripts/ingest_sec_company.py --ticker AAPL
python scripts/ingest_sec_company.py --ticker MSFT
python scripts/ingest_sec_company.py --all
```

Run manually from the Ubuntu VM clone:

```bash
cd /home/julio/FinAgentOps
/home/julio/FinAgentOps/.venv/bin/python scripts/ingest_sec_company.py --ticker AAPL
/home/julio/FinAgentOps/.venv/bin/python scripts/ingest_sec_company.py --ticker MSFT
/home/julio/FinAgentOps/.venv/bin/python scripts/ingest_sec_company.py --all
```

When `--ticker` is used, the script ingests one supported company. When `--all` is used, the script loops through every company in `company_universe.py`.

For each company, the script performs four steps:

1. Fetch the public SEC company facts JSON.
2. Store the untouched response in `raw_sec_company_facts`.
3. Extract annual `10-K` facts into `financial_facts`.
4. Update or insert yearly rows in `financial_metrics`.

The ingestion is idempotent. Running the same ticker again updates the raw SEC response, extracted facts, and yearly metrics instead of creating duplicate yearly metric rows.

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

## Local Cron Schedule

The Ubuntu VM has a local Linux cron job that runs the full configured SEC company universe every day at `06:00` VM time:

```cron
0 6 * * * cd /home/julio/FinAgentOps && echo "========== $(date '+\%Y-\%m-\%d \%H:\%M:\%S') START SEC ingestion ALL ==========" >> /home/julio/FinAgentOps/logs/sec_ingestion.log && /home/julio/FinAgentOps/.venv/bin/python scripts/ingest_sec_company.py --all >> /home/julio/FinAgentOps/logs/sec_ingestion.log 2>&1 && echo "========== $(date '+\%Y-\%m-\%d \%H:\%M:\%S') END SEC ingestion ALL ==========" >> /home/julio/FinAgentOps/logs/sec_ingestion.log
```

Cron field meaning:

- `0` means minute zero.
- `6` means hour six.
- `* * *` means every day of the month, every month, every day of the week.

In plain English, this means: run once per day at `06:00` according to the VM's local timezone.

The command does three operationally useful things:

1. Changes into `/home/julio/FinAgentOps` so relative paths work.
2. Appends a timestamped start line to `logs/sec_ingestion.log`.
3. Runs the ingestion script and appends normal output and errors to the same log file.
4. Appends a timestamped end line when the ingestion command succeeds.

Check the cron log from inside the VM:

```bash
tail -n 100 /home/julio/FinAgentOps/logs/sec_ingestion.log
```

Follow the log live while testing:

```bash
tail -f /home/julio/FinAgentOps/logs/sec_ingestion.log
```

This is a local development scheduler. It is useful for learning and proving the pipeline works end to end, but it is not the final production scheduler. Later, the ingestion can be migrated to a cloud-native schedule such as GitHub Actions scheduled workflows, Google Cloud Scheduler plus Cloud Run Jobs, or another managed orchestration tool.

## Verification Queries

After running the ingestion, connect to PostgreSQL and verify the raw payload:

```sql
SELECT
	  ticker
	, name
	, exchange
	, sector
FROM companies
WHERE ticker IN (
	  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'
	, 'META', 'AVGO', 'TSLA', 'BRK.B', 'LLY'
	, 'JPM', 'WMT', 'V', 'ORCL', 'MA'
)
ORDER BY ticker;
```

Verify raw SEC payloads:

```sql
SELECT
	  ticker
	, cik
	, fetched_at
FROM raw_sec_company_facts
WHERE ticker IN (
	  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'
	, 'META', 'AVGO', 'TSLA', 'BRK.B', 'LLY'
	, 'JPM', 'WMT', 'V', 'ORCL', 'MA'
)
ORDER BY ticker;
```

Verify extracted facts:

```sql
SELECT
	  ticker
	, COUNT(*) AS fact_rows
	, MIN(fiscal_year) AS first_year
	, MAX(fiscal_year) AS latest_year
FROM financial_facts
WHERE ticker IN (
	  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'
	, 'META', 'AVGO', 'TSLA', 'BRK.B', 'LLY'
	, 'JPM', 'WMT', 'V', 'ORCL', 'MA'
)
GROUP BY ticker
ORDER BY ticker;
```

Inspect extracted fact details for one company:

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
	  c.ticker
	, COUNT(*) AS metric_rows
	, MIN(fm.fiscal_year) AS first_year
	, MAX(fm.fiscal_year) AS latest_year
FROM financial_metrics fm
JOIN companies c
	ON c.id = fm.company_id
WHERE c.ticker IN (
	  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'
	, 'META', 'AVGO', 'TSLA', 'BRK.B', 'LLY'
	, 'JPM', 'WMT', 'V', 'ORCL', 'MA'
)
GROUP BY c.ticker
ORDER BY c.ticker;
```

Verify metric row coverage by company:

```sql
SELECT
	  com.ticker
	, COUNT( met.id )        AS metric_rows
	, MIN( met.fiscal_year ) AS first_year
	, MAX( met.fiscal_year ) AS latest_year
FROM
	public.companies  com
LEFT JOIN
	public.financial_metrics  met
	ON com.id = met.company_id
GROUP BY
	  com.ticker
ORDER BY
	  com.ticker
;
```

Inspect transformed yearly metrics for one company:

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
	, fm.created_at
	, fm.updated_at
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

For a quick success/failure check of the scheduled job, filter to the SEC source:

```sql
SELECT
	  source_name
	, status
	, started_at
	, finished_at
	, records_processed
	, error_message
FROM pipeline_runs
WHERE source_name = 'sec_companyfacts_aapl'
ORDER BY last_run_at DESC
LIMIT 10;
```

For a multi-company run, check all SEC companyfacts sources:

```sql
SELECT
	  source_name
	, status
	, started_at
	, finished_at
	, records_processed
	, error_message
FROM pipeline_runs
WHERE source_name IN (
	  'sec_companyfacts_aapl'
	, 'sec_companyfacts_msft'
	, 'sec_companyfacts_googl'
	, 'sec_companyfacts_amzn'
	, 'sec_companyfacts_nvda'
	, 'sec_companyfacts_meta'
	, 'sec_companyfacts_avgo'
	, 'sec_companyfacts_tsla'
	, 'sec_companyfacts_brk.b'
	, 'sec_companyfacts_lly'
	, 'sec_companyfacts_jpm'
	, 'sec_companyfacts_wmt'
	, 'sec_companyfacts_v'
	, 'sec_companyfacts_orcl'
	, 'sec_companyfacts_ma'
)
ORDER BY last_run_at DESC
LIMIT 25;
```

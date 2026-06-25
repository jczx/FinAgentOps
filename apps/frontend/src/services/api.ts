import type {
	Company,
	CompanyComparison,
	Kpi,
	PipelineRun,
	PipelineStatus,
	YearlyFinancialMetric,
} from "../data/dashboardTypes";

const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ApiCompany = {
	name: string;
	ticker: string;
	exchange: string;
	sector: string;
};

type ApiYearlyFinancialMetric = {
	ticker: string;
	company_name: string;
	fiscal_year: number | null;
	fiscal_period: string;
	revenue: number | null;
	net_income: number | null;
	total_assets: number | null;
	total_liabilities: number | null;
	operating_cash_flow: number | null;
	profit_margin: number;
	debt_to_assets_ratio: number | null;
	return_on_assets: number | null;
	operating_cash_flow_margin: number | null;
	revenue_growth: number;
	net_income_growth: number | null;
	created_at: string | null;
	updated_at: string | null;
};

type ApiMetricsResponse = {
	ticker: string;
	company_name: string;
	metrics: ApiMetric[];
	yearly_metrics: ApiYearlyFinancialMetric[];
};

type ApiComparisonItem = {
	ticker: string;
	company_name: string;
	latest_metric: ApiYearlyFinancialMetric | null;
	yearly_metrics: ApiYearlyFinancialMetric[];
};

type ApiComparisonResponse = {
	requested_tickers: string[];
	missing_tickers: string[];
	companies: ApiComparisonItem[];
};

type ApiMetric = {
	label: string;
	value: number;
	unit: string;
	description: string;
};

type ApiPipelineRun = {
	source_name: string;
	status: string;
	started_at: string | null;
	finished_at: string | null;
	records_processed: number;
	error_message: string;
	message: string;
};

type ApiPipelineStatusResponse = {
	status: string;
	last_run: string;
	steps_completed: number;
	total_steps: number;
	message: string;
	runs: ApiPipelineRun[];
};

export type DashboardApiData = {
	companies: Company[];
	company: Company;
	kpis: Kpi[];
	yearlyMetrics: YearlyFinancialMetric[];
	pipeline: PipelineStatus;
};

async function getJson<T>(path: string): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${path}`);

	if (!response.ok) {
		throw new Error(`Request failed: ${response.status} ${response.statusText}`);
	}

	return response.json() as Promise<T>;
}

function mapCompany(company: ApiCompany): Company {
	return {
		name: company.name,
		ticker: company.ticker,
		exchange: company.exchange,
		sector: company.sector,
	};
}

function mapYearlyMetric(
	metric: ApiYearlyFinancialMetric,
): YearlyFinancialMetric {
	return {
		ticker: metric.ticker,
		companyName: metric.company_name,
		fiscalYear: metric.fiscal_year,
		fiscalPeriod: metric.fiscal_period,
		revenue: metric.revenue,
		netIncome: metric.net_income,
		totalAssets: metric.total_assets,
		totalLiabilities: metric.total_liabilities,
		operatingCashFlow: metric.operating_cash_flow,
		profitMargin: metric.profit_margin,
		debtToAssetsRatio: metric.debt_to_assets_ratio,
		returnOnAssets: metric.return_on_assets,
		operatingCashFlowMargin: metric.operating_cash_flow_margin,
		revenueGrowth: metric.revenue_growth,
		netIncomeGrowth: metric.net_income_growth,
		createdAt: metric.created_at,
		updatedAt: metric.updated_at,
	};
}

function mapPipelineRun(run: ApiPipelineRun): PipelineRun {
	return {
		sourceName: run.source_name,
		status: run.status,
		startedAt: run.started_at,
		finishedAt: run.finished_at,
		recordsProcessed: run.records_processed,
		errorMessage: run.error_message,
		message: run.message,
	};
}

function formatCurrency(value: number | null): string {
	if (value === null) {
		return "Not available";
	}

	return new Intl.NumberFormat("en-US", {
		compactDisplay: "short",
		currency: "USD",
		maximumFractionDigits: 1,
		notation: "compact",
		style: "currency",
	}).format(value);
}

function formatPercent(value: number | null): string {
	if (value === null) {
		return "Not available";
	}

	return `${value.toFixed(1)}%`;
}

function metricTrend(value: number | null, lowerIsBetter = false): Kpi["trend"] {
	if (value === null || value === 0) {
		return "flat";
	}

	if (lowerIsBetter) {
		return value > 0 ? "down" : "up";
	}

	return value > 0 ? "up" : "down";
}

function buildKpis(latestMetric: YearlyFinancialMetric | undefined): Kpi[] {
	if (!latestMetric) {
		return [];
	}

	return [
		{
			label: "Revenue",
			value: formatCurrency(latestMetric.revenue),
			description: `Total revenue for ${latestMetric.fiscalPeriod}.`,
			trend: metricTrend(latestMetric.revenueGrowth),
		},
		{
			label: "Net income",
			value: formatCurrency(latestMetric.netIncome),
			description: `Net income for ${latestMetric.fiscalPeriod}.`,
			trend: metricTrend(latestMetric.netIncomeGrowth),
		},
		{
			label: "Total assets",
			value: formatCurrency(latestMetric.totalAssets),
			description: `Assets reported for ${latestMetric.fiscalPeriod}.`,
			trend: "flat",
		},
		{
			label: "Debt-to-assets",
			value: formatPercent(latestMetric.debtToAssetsRatio),
			description: "Total liabilities as a share of total assets.",
			trend: metricTrend(latestMetric.debtToAssetsRatio, true),
		},
		{
			label: "Profit margin",
			value: formatPercent(latestMetric.profitMargin),
			description: "Net income as a share of revenue.",
			trend: metricTrend(latestMetric.profitMargin),
		},
		{
			label: "Return on assets",
			value: formatPercent(latestMetric.returnOnAssets),
			description: "Net income as a share of total assets.",
			trend: metricTrend(latestMetric.returnOnAssets),
		},
	];
}

export async function fetchCompanies(): Promise<Company[]> {
	const companies = await getJson<ApiCompany[]>("/companies");
	return companies.map(mapCompany);
}

export async function fetchCompanyMetrics(
	ticker: string,
): Promise<CompanyComparison> {
	const metricsResponse = await getJson<ApiMetricsResponse>(
		`/companies/${ticker}/metrics`,
	);
	const yearlyMetrics = metricsResponse.yearly_metrics.map(mapYearlyMetric);

	return {
		ticker: metricsResponse.ticker,
		companyName: metricsResponse.company_name,
		latestMetric: yearlyMetrics[yearlyMetrics.length - 1] ?? null,
		yearlyMetrics,
	};
}

export async function fetchComparisonData(
	tickers: string[],
): Promise<CompanyComparison[]> {
	const uniqueTickers = [...new Set(tickers.map((ticker) => ticker.toUpperCase()))];
	if (uniqueTickers.length === 0) {
		return [];
	}

	const response = await getJson<ApiComparisonResponse>(
		`/companies/comparison?tickers=${encodeURIComponent(uniqueTickers.join(","))}`,
	);

	return response.companies.map((company) => {
		const yearlyMetrics = company.yearly_metrics.map(mapYearlyMetric);

		return {
			ticker: company.ticker,
			companyName: company.company_name,
			latestMetric: company.latest_metric
				? mapYearlyMetric(company.latest_metric)
				: null,
			yearlyMetrics,
		};
	});
}

export async function fetchDashboardData(
	ticker: string,
): Promise<DashboardApiData> {
	try {
		const [companies, company, metricsResponse, pipelineResponse] =
			await Promise.all([
				fetchCompanies(),
				getJson<ApiCompany>(`/companies/${ticker}`),
				getJson<ApiMetricsResponse>(`/companies/${ticker}/metrics`),
				getJson<ApiPipelineStatusResponse>("/pipeline/status"),
			]);

		const yearlyMetrics = metricsResponse.yearly_metrics.map(mapYearlyMetric);
		const latestMetric = yearlyMetrics[yearlyMetrics.length - 1];

		return {
			companies,
			company: mapCompany(company),
			kpis: buildKpis(latestMetric),
			yearlyMetrics,
			pipeline: {
				status: pipelineResponse.status,
				lastRun: pipelineResponse.last_run,
				stepsCompleted: pipelineResponse.steps_completed,
				totalSteps: pipelineResponse.total_steps,
				message: pipelineResponse.message,
				runs: pipelineResponse.runs.map(mapPipelineRun),
			},
		};
	} catch (error) {
		console.error(error);
		throw new Error(
			"Unable to load financial data. Make sure the FastAPI backend is running and PostgreSQL is reachable.",
		);
	}
}

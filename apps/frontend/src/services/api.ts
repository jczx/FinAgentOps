import type {
	Company,
	Kpi,
	PipelineStatus,
	RiskProfile,
} from "../data/dashboardTypes";

const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ApiMetric = {
	label: string;
	value: number;
	unit: string;
	description: string;
};

type ApiMetricsResponse = {
	ticker: string;
	metrics: ApiMetric[];
};

type ApiRiskScoreResponse = {
	ticker: string;
	risk_score: RiskProfile["score"];
	summary: string;
	factors: string[];
};

type ApiPipelineStatusResponse = {
	status: PipelineStatus["status"];
	last_run: string;
	steps_completed: number;
	total_steps: number;
	message: string;
};

export type DashboardApiData = {
	company: Company;
	kpis: Kpi[];
	risk: RiskProfile;
	pipeline: PipelineStatus;
};

async function getJson<T>(path: string): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${path}`);

	if (!response.ok) {
		throw new Error(`Request failed: ${response.status} ${response.statusText}`);
	}

	return response.json() as Promise<T>;
}

function formatMetricValue(metric: ApiMetric): string {
	if (metric.unit === "percent") {
		return `${metric.value.toFixed(1)}%`;
	}

	return String(metric.value);
}

function metricTrend(label: string): Kpi["trend"] {
	if (label.toLowerCase().includes("debt")) {
		return "down";
	}

	return label.toLowerCase().includes("profit") ? "flat" : "up";
}

function mapMetricToKpi(metric: ApiMetric): Kpi {
	return {
		label: metric.label,
		value: formatMetricValue(metric),
		description: metric.description,
		trend: metricTrend(metric.label),
	};
}

export async function fetchDashboardData(ticker: string): Promise<DashboardApiData> {
	try {
		const [company, metricsResponse, riskResponse, pipelineResponse] =
			await Promise.all([
				getJson<Company>(`/companies/${ticker}`),
				getJson<ApiMetricsResponse>(`/companies/${ticker}/metrics`),
				getJson<ApiRiskScoreResponse>(`/companies/${ticker}/risk-score`),
				getJson<ApiPipelineStatusResponse>("/pipeline/status"),
			]);

		return {
			company,
			kpis: metricsResponse.metrics.map(mapMetricToKpi),
			risk: {
				score: riskResponse.risk_score,
				summary: riskResponse.summary,
				factors: riskResponse.factors,
			},
			pipeline: {
				status: pipelineResponse.status,
				lastRun: pipelineResponse.last_run,
				stepsCompleted: pipelineResponse.steps_completed,
				totalSteps: pipelineResponse.total_steps,
			},
		};
	} catch (error) {
		console.error(error);
		throw new Error(
			"Unable to load dashboard data. Make sure the FastAPI backend is running at " +
				`${API_BASE_URL}.`,
		);
	}
}

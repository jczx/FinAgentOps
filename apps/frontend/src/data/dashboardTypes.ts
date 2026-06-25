export type Company = {
	name: string;
	ticker: string;
	exchange: string;
	sector: string;
};

export type Kpi = {
	label: string;
	value: string;
	description: string;
	trend: "up" | "down" | "flat";
};

export type YearlyFinancialMetric = {
	ticker: string;
	companyName: string;
	fiscalYear: number | null;
	fiscalPeriod: string;
	revenue: number | null;
	netIncome: number | null;
	totalAssets: number | null;
	totalLiabilities: number | null;
	operatingCashFlow: number | null;
	profitMargin: number;
	debtToAssetsRatio: number | null;
	returnOnAssets: number | null;
	operatingCashFlowMargin: number | null;
	revenueGrowth: number;
	netIncomeGrowth: number | null;
	createdAt: string | null;
	updatedAt: string | null;
};

export type CompanyComparison = {
	ticker: string;
	companyName: string;
	latestMetric: YearlyFinancialMetric | null;
	yearlyMetrics: YearlyFinancialMetric[];
};

export type PipelineStatus = {
	status: string;
	lastRun: string;
	stepsCompleted: number;
	totalSteps: number;
	message: string;
	runs: PipelineRun[];
};

export type PipelineRun = {
	sourceName: string;
	status: string;
	startedAt: string | null;
	finishedAt: string | null;
	recordsProcessed: number;
	errorMessage: string;
	message: string;
};

export type AnalystMessage = {
	role: "assistant" | "user";
	text: string;
};

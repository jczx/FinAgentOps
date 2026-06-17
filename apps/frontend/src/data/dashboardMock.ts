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

export type RiskProfile = {
	score: "Low" | "Medium" | "High";
	summary: string;
	factors: string[];
};

export type PipelineStatus = {
	status: "Success" | "Warning" | "Failed";
	lastRun: string;
	stepsCompleted: number;
	totalSteps: number;
};

export type TrendPoint = {
	label: string;
	value: number;
};

export type AnalystMessage = {
	role: "assistant" | "user";
	text: string;
};

export type DashboardMock = {
	company: Company;
	kpis: Kpi[];
	risk: RiskProfile;
	pipeline: PipelineStatus;
	trend: TrendPoint[];
	analyst: AnalystMessage[];
};

export const dashboardMock: DashboardMock = {
	company: {
		name: "Apple Inc.",
		ticker: "AAPL",
		exchange: "NASDAQ",
		sector: "Technology",
	},
	kpis: [
		{
			label: "Revenue growth",
			value: "8.2%",
			description: "Year-over-year top-line growth",
			trend: "up",
		},
		{
			label: "Profit margin",
			value: "22.5%",
			description: "Net income as a share of revenue",
			trend: "flat",
		},
		{
			label: "Debt-to-assets",
			value: "31.4%",
			description: "Debt compared with total assets",
			trend: "down",
		},
		{
			label: "Free cash flow margin",
			value: "18.7%",
			description: "Free cash flow as a share of revenue",
			trend: "up",
		},
	],
	risk: {
		score: "Low",
		summary:
			"Mock analysis indicates stable profitability, strong cash flow, and manageable leverage.",
		factors: ["Positive free cash flow", "Healthy margins", "Moderate debt load"],
	},
	pipeline: {
		status: "Success",
		lastRun: "Mock run",
		stepsCompleted: 4,
		totalSteps: 4,
	},
	trend: [
		{ label: "Q1", value: 62 },
		{ label: "Q2", value: 68 },
		{ label: "Q3", value: 72 },
		{ label: "Q4", value: 77 },
	],
	analyst: [
		{
			role: "assistant",
			text: "The AI analyst will summarize financial signals after RAG is added.",
		},
		{
			role: "user",
			text: "What changed in revenue growth this quarter?",
		},
	],
};
